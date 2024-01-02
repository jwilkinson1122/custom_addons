# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.tools import float_compare

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_order_ids = fields.One2many(
        comodel_name='prescription.order', inverse_name='sale_order_id',
        string='Prescription Order', groups='stock.group_stock_user')
    prescription_count = fields.Integer(
        "Prescription Order(s)", compute='_compute_prescription_count', groups='stock.group_stock_user')

    @api.depends('prescription_order_ids')
    def _compute_prescription_count(self):
        for order in self:
            order.prescription_count = len(order.prescription_order_ids)

    def _action_cancel(self):
        res = super()._action_cancel()
        self.order_line._cancel_prescription_order()
        return res

    def _action_confirm(self):
        res = super()._action_confirm()
        self.order_line._create_prescription_order()
        return res

    def action_show_prescription(self):
        self.ensure_one()
        if self.prescription_count == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "prescription.order",
                "views": [[False, "form"]],
                "res_id": self.prescription_order_ids.id,
            }
        elif self.prescription_count > 1:
            return {
                "name": _("Prescription Orders"),
                "type": "ir.actions.act_window",
                "res_model": "prescription.order",
                "view_mode": "tree,form",
                "domain": [('sale_order_id', '=', self.id)],
            }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_qty_delivered(self):
        remaining_so_lines = self
        for so_line in self:
            move = so_line.move_ids.sudo().filtered(lambda m: m.prescription_id and m.state == 'done')
            if len(move) != 1:
                continue
            remaining_so_lines -= so_line
            so_line.qty_delivered = move.quantity
        return super(SaleOrderLine, remaining_so_lines)._compute_qty_delivered()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.filtered(lambda line: line.state in ('sale', 'done'))._create_prescription_order()
        return res

    def write(self, vals_list):
        old_product_uom_qty = {line.id: line.product_uom_qty for line in self}
        res = super().write(vals_list)
        for line in self:
            if line.state in ('sale', 'done'):
                if float_compare(old_product_uom_qty[line.id], 0, precision_rounding=line.product_uom.rounding) <= 0 and float_compare(line.product_uom_qty, 0, precision_rounding=line.product_uom.rounding) > 0:
                    self._create_prescription_order()
                if float_compare(old_product_uom_qty[line.id], 0, precision_rounding=line.product_uom.rounding) > 0 and float_compare(line.product_uom_qty, 0, precision_rounding=line.product_uom.rounding) <= 0:
                    self._cancel_prescription_order()
        return res

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Picking must be generated for products created from the SO but not for parts added from the RX, as they're already handled there
        lines_without_prescription_move = self.filtered(lambda line: not line.move_ids.sudo().prescription_id)
        return super(SaleOrderLine, lines_without_prescription_move)._action_launch_stock_rule(previous_product_uom_qty)

    def _create_prescription_order(self):
        new_prescription_vals = []
        for line in self:
            # One RX for each line with at least a quantity of 1, quantities > 1 don't create multiple RXs
            if any(line.id == rx.sale_order_line_id.id for rx in line.order_id.sudo().prescription_order_ids) and float_compare(line.product_uom_qty, 0, precision_rounding=line.product_uom.rounding) > 0:
                binded_rx_ids = line.order_id.sudo().prescription_order_ids.filtered(lambda rx: rx.sale_order_line_id.id == line.id and rx.state == 'cancel')
                binded_rx_ids.action_prescription_cancel_draft()
                binded_rx_ids._action_prescription_confirm()
                continue
            if not line.product_template_id.sudo().create_prescription or line.move_ids.sudo().prescription_id or float_compare(line.product_uom_qty, 0, precision_rounding=line.product_uom.rounding) <= 0:
                continue
            order = line.order_id
            new_prescription_vals.append({
                'state': 'confirmed',
                'partner_id': order.partner_id.id,
                'sale_order_id': order.id,
                'sale_order_line_id': line.id,
                'picking_type_id': order.warehouse_id.prescription_type_id.id,
            })
            if line.product_template_id.type in ('consu', 'product'):
                new_prescription_vals[-1].update({
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                })

        if new_prescription_vals:
            self.env['prescription.order'].sudo().create(new_prescription_vals)

    def _cancel_prescription_order(self):
        # Each RX binded to a SO line with Qty set to 0 or cancelled is set to 'Cancelled'
        binded_rx_ids = self.env['prescription.order']
        for line in self:
            binded_rx_ids |= line.order_id.sudo().prescription_order_ids.filtered(lambda rx: rx.sale_order_line_id.id == line.id and rx.state != 'done')
        binded_rx_ids.action_prescription_cancel()

    def has_valued_move_ids(self):
        res = super().has_valued_move_ids()
        return res and not self.move_ids.prescription_id
