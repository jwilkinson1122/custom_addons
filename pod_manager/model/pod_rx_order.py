# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class pod_rx_order(models.Model):
    _name = "pod.rx.order"
    _description = 'podiatry Rx Order order'

    name = fields.Char('Rx Order ID')
    # patient_id = fields.Many2one('pod.patient', 'Patient')
    patient_id = fields.Many2one(
        'pod.patient', string="Patient", required=True)

    ship_to_patient = fields.Boolean(
        string="Ship to Patient",
        help="Indicates if order ships to patient",
    )

    rx_date = fields.Datetime(
        'Rx Order Date', default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', 'Login User', readonly=True, default=lambda self: self.env.user)
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.invoice', 'Invoice')

    # doctor_id = fields.Many2one('pod.doctor', 'Prescribing Doctor')
#  doctor_id = fields.Many2one('pod.doctor', string="Doctor", required=True)
    doctor_id = fields.Many2one(
        'res.partner', domain=[('is_doctor', '=', True)], string="Prescribing Doctor", )

    state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')
    # pharmacy_partner_id = fields.Many2one(
    #     'res.partner', domain=[('is_pharmacy', '=', True)], string='Pharmacy')
    rx_line_ids = fields.One2many(
        'pod.rx.order.line', 'name', 'Rx Order Line')
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Rx Order Note')
    is_invoiced = fields.Boolean(copy=False, default=False)
    is_shipped = fields.Boolean(default=False, copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'pod.rx.order') or '/'
        return super(pod_rx_order, self).create(vals)

    def rx_report(self):
        return self.env.ref('pod_manager.report_print_rx').report_action(self)

    # @api.onchange('name')
    # def onchange_name(self):
    #     ins_obj = self.env['pod.insurance']
    #     ins_record = ins_obj.search(
    #         [('pod_insurance_partner_id', '=', self.patient_id.patient_id.id)])
    #     self.insurer_id = ins_record.id or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
