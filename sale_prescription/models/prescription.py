# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Prescription(models.Model):
    _inherit = "prescription"

    sale_order_count = fields.Integer(
        "Number of Source Sale",
        compute='_compute_sale_order_count',
        groups='sales_team.group_sale_salesman')

    @api.depends('order_line.sale_order_id')
    def _compute_sale_order_count(self):
        for prescription in self:
            prescription.sale_order_count = len(prescription._get_sale_orders())

    def action_view_sale_orders(self):
        self.ensure_one()
        sale_order_ids = self._get_sale_orders().ids
        action = {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
        if len(sale_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': sale_order_ids[0],
            })
        else:
            action.update({
                'name': _('Sources Sale Orders %s', self.name),
                'domain': [('id', 'in', sale_order_ids)],
                'view_mode': 'tree,form',
            })
        return action

    def button_cancel(self):
        result = super(Prescription, self).button_cancel()
        self.sudo()._activity_cancel_on_sale()
        return result

    def _get_sale_orders(self):
        return self.order_line.sale_order_id

    def _activity_cancel_on_sale(self):
        """ If some PO are cancelled, we need to put an activity on their origin SO (only the open ones). Since a PO can have
            been modified by several SO, when cancelling one PO, many next activities can be schedulded on different SO.
        """
        sale_to_notify_map = {}  # map SO -> recordset of PO as {sale.order: set(prescription.line)}
        for order in self:
            for prescription_line in order.order_line:
                if prescription_line.sale_line_id:
                    sale_order = prescription_line.sale_line_id.order_id
                    sale_to_notify_map.setdefault(sale_order, self.env['prescription.line'])
                    sale_to_notify_map[sale_order] |= prescription_line

        for sale_order, prescription_lines in sale_to_notify_map.items():
            sale_order._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=sale_order.user_id.id or self.env.uid,
                views_or_xmlid='sale_prescription.exception_sale_on_prescription_cancellation',
                render_context={
                    'prescriptions': prescription_lines.mapped('order_id'),
                    'prescription_lines': prescription_lines,
            })


class PrescriptionLine(models.Model):
    _inherit = 'prescription.line'

    sale_order_id = fields.Many2one(related='sale_line_id.order_id', string="Sale Order", store=True, readonly=True)
    sale_line_id = fields.Many2one('sale.order.line', string="Origin Sale Item", index='btree_not_null', copy=False)