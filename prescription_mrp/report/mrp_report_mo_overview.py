# -*- coding: utf-8 -*-


from odoo import fields, models

class ReportMoOverview(models.AbstractModel):
    _inherit = 'report.mrp.report_mo_overview'

    def _get_extra_replenishments(self, product):
        res = super()._get_extra_replenishments(product)
        domain = [('state', 'in', ['draft', 'sent', 'to approve']), ('product_id', '=', product.id)]
        warehouse_id = self.env.context.get('warehouse', False)
        if warehouse_id:
            domain += [('order_id.picking_type_id.warehouse_id', '=', warehouse_id)]
        rx_lines = self.env['prescription.order.line'].search(domain, order='date_planned, id')

        for rx_line in rx_lines:
            line_qty = rx_line.product_qty
            for move in rx_line.move_dest_ids:
                linked_production = self.env['stock.move'].browse(move._rollup_move_dests()).raw_material_production_id
                # Only create specific lines for moves directly linked to a manufacturing order
                if not linked_production:
                    continue
                prod_qty = min(line_qty, move.product_uom._compute_quantity(move.product_uom_qty, rx_line.product_uom))
                res.append(self._format_extra_replenishment(rx_line, prod_qty, linked_production.id))
                line_qty -= prod_qty
            if line_qty:
                res.append(self._format_extra_replenishment(rx_line, line_qty))

        return res

    def _format_extra_replenishment(self, rx_line, quantity, production_id=False):
        rx = rx_line.order_id
        price = rx_line.taxes_id.with_context(round=False).compute_all(
            rx_line.price_unit, currency=rx.currency_id, quantity=quantity, product=rx_line.product_id, partner=rx.partner_id
        )['total_void']
        return {
            '_name': 'prescription.order',
            'id': rx.id,
            'cost': price,
            'quantity': quantity,
            'uom': rx_line.product_uom,
            'production_id': production_id
        }

    def _get_replenishment_receipt(self, doc_in, components):
        res = super()._get_replenishment_receipt(doc_in, components)
        if doc_in._name == 'prescription.order':
            if doc_in.state != 'prescription':
                return self._format_receipt_date('estimated', doc_in.date_planned)
            in_pickings = doc_in.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
            planned_date = max(in_pickings.mapped('scheduled_date')) if in_pickings else doc_in.date_planned
            return self._format_receipt_date('expected', planned_date)
        return res

    def _get_resupply_data(self, rules, rules_delay, quantity, uom_id, product, production):
        res = super()._get_resupply_data(rules, rules_delay, quantity, uom_id, product, production)
        if any(rule for rule in rules if rule.action == 'buy' and product.seller_ids):
            supplier = product._select_seller(quantity=quantity, uom_id=product.uom_id)
            if supplier:
                return {
                    'delay': supplier.delay + rules_delay,
                    'cost': supplier.price * uom_id._compute_quantity(quantity, supplier.product_uom),
                    'currency': supplier.currency_id,
                }
        return res

    def _is_doc_in_done(self, doc_in):
        if doc_in._name == 'prescription.order':
            return doc_in.state == 'prescription' and all(move.state in ('done', 'cancel') for move in doc_in.order_line.move_ids)
        return super()._is_doc_in_done(doc_in)

    def _get_origin(self, move):
        if move.prescription_line_id:
            return move.prescription_line_id.order_id
        return super()._get_origin(move)

    def _get_replenishment_mo_cost(self, product, quantity, uom_id, currency, move_in=False):
        if move_in and move_in.prescription_line_id:
            rx_line = move_in.prescription_line_id
            rx = rx_line.order_id
            price = rx_line.taxes_id.with_context(round=False).compute_all(
                rx_line.price_unit, currency=rx.currency_id, quantity=uom_id._compute_quantity(quantity, move_in.prescription_line_id.product_uom),
                product=rx_line.product_id, partner=rx.partner_id
            )['total_void']
            price = rx_line.currency_id._convert(price, currency, (move_in.company_id or self.env.company), fields.Date.today())
            return currency.round(price)
        return super()._get_replenishment_mo_cost(product, quantity, uom_id, currency, move_in)
