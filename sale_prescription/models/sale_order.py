# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_count = fields.Integer(
        "Number of Prescription Order Generated",
        compute='_compute_prescription_count',
        groups='prescription.group_prescription_user')

    @api.depends('order_line.prescription_line_ids.order_id')
    def _compute_prescription_count(self):
        for order in self:
            order.prescription_count = len(order._get_prescriptions())

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self:
            order.order_line.sudo()._prescription_service_generation()
        return result

    def _action_cancel(self):
        result = super()._action_cancel()
        # When a sale person cancel a SO, he might not have the rights to write
        # on PO. But we need the system to create an activity on the PO (so 'write'
        # access), hence the `sudo`.
        self.sudo()._activity_cancel_on_prescription()
        return result

    def action_view_prescriptions(self):
        self.ensure_one()
        prescription_ids = self._get_prescriptions().ids
        action = {
            'res_model': 'prescription',
            'type': 'ir.actions.act_window',
        }
        if len(prescription_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': prescription_ids[0],
            })
        else:
            action.update({
                'name': _("Prescription Order generated from %s", self.name),
                'domain': [('id', 'in', prescription_ids)],
                'view_mode': 'tree,form',
            })
        return action

    def _get_prescriptions(self):
        return self.order_line.prescription_line_ids.order_id

    def _activity_cancel_on_prescription(self):
        """ If some SO are cancelled, we need to put an activity on their generated prescription. If sale lines of
            different sale orders impact different prescription, we only want one activity to be attached.
        """
        prescription_to_notify_map = {}  # map PO -> recordset of SOL as {prescription: set(sale.orde.liner)}

        prescription_lines = self.env['prescription.line'].search([('sale_line_id', 'in', self.mapped('order_line').ids), ('state', '!=', 'cancel')])
        for prescription_line in prescription_lines:
            prescription_to_notify_map.setdefault(prescription_line.order_id, self.env['sale.order.line'])
            prescription_to_notify_map[prescription_line.order_id] |= prescription_line.sale_line_id

        for prescription, sale_order_lines in prescription_to_notify_map.items():
            prescription._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=prescription.user_id.id or self.env.uid,
                views_or_xmlid='sale_prescription.exception_prescription_on_sale_cancellation',
                render_context={
                    'sale_orders': sale_order_lines.mapped('order_id'),
                    'sale_order_lines': sale_order_lines,
            })
