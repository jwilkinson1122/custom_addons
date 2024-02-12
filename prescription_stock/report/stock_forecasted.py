# -*- coding: utf-8 -*-


from odoo import models


class StockForecasted(models.AbstractModel):
    _inherit = 'stock.forecasted_product_product'

    def _prepare_report_line(self, quantity, move_out=None, move_in=None, replenishment_filled=True, product=False, reserved_move=False, in_transit=False, read=True):
        line = super()._prepare_report_line(quantity, move_out, move_in, replenishment_filled, product, reserved_move, in_transit, read)

        if not move_out or not move_out.picking_id or not move_out.picking_id.prescription_id:
            return line

        picking = move_out.picking_id
        line['move_out'].update({
            'picking_id' : {
                'id' : picking.id,
                'priority' : picking.priority,
                'prescription_id' : {
                    'id' : picking.prescription_id.id,
                    'amount_untaxed' : picking.prescription_id.amount_untaxed,
                    'currency_id' : picking.prescription_id.currency_id.read(fields=['id', 'name'])[0] if read else picking.prescription_id.currency_id,
                    'partner_id' : picking.prescription_id.partner_id.read(fields=['id', 'name'])[0] if read else picking.prescription_id.partner_id,
                }
            }
        })
        return line

    def _get_report_header(self, product_template_ids, product_ids, wh_location_ids):
        res = super()._get_report_header(product_template_ids, product_ids, wh_location_ids)
        domain = self._product_prescription_domain(product_template_ids, product_ids)
        so_lines = self.env['prescription.line'].search(domain)
        out_sum = 0
        if so_lines:
            product_uom = so_lines[0].product_id.uom_id
            quantities = so_lines.mapped(lambda line: line.product_uom._compute_quantity(line.product_uom_qty, product_uom))
            out_sum = sum(quantities)
        res['draft_prescription_qty'] = out_sum
        res['draft_prescriptions'] = so_lines.mapped("order_id").sorted(key=lambda so: so.name).read(fields=['id', 'name'])
        res['draft_prescriptions_matched'] = self.env.context.get('prescription_line_to_match_id') in so_lines.ids
        res['qty']['out'] += out_sum
        return res

    def _product_prescription_domain(self, product_template_ids, product_ids):
        domain = [('state', 'in', ['draft', 'sent'])]
        if product_template_ids:
            domain += [('product_template_id', 'in', product_template_ids)]
        elif product_ids:
            domain += [('product_id', 'in', product_ids)]
        warehouse_id = self.env.context.get('warehouse', False)
        if warehouse_id:
            domain += [('warehouse_id', '=', warehouse_id)]
        return domain