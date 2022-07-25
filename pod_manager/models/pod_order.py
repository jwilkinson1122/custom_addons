# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class pod_order(models.Model):
    _name = "pod.order"
    _description = 'pod order'

    name = fields.Char('Order ID')
    pod_patient_id = fields.Many2one('pod.patient', 'Patient ID')
    pod_order_date = fields.Datetime(
        'Order Date', default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', 'Login User', readonly=True, default=lambda self: self.env.user)
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.invoice', 'Invoice')
    invoice_to_insurer = fields.Boolean('Invoice to Insurance')
    doctor_id = fields.Many2one('pod.doctor', 'Prescribing Doctor')

    state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')

    pod_oder_detail_ids = fields.One2many(
        'pod_order.line', 'name', 'Order Line')
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Order Note')

    is_invoiced = fields.Boolean(copy=False, default=False)

    is_shipped = fields.Boolean(default=False, copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'pod.order') or '/'
        return super(pod_order, self).create(vals)

    def pod_order_report(self):
        return self.env.ref('pod_manager.report_print_pod_order').report_action(self)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
