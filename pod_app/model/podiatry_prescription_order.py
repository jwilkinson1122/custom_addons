# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_prescription_order(models.Model):
    _name = "podiatry.prescription.order"
    _description = 'podiatry Prescription order'

    name = fields.Char('Prescription ID')
    patient_id = fields.Many2one('podiatry.patient', 'Patient ID')
    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', 'Login User', readonly=True, default=lambda self: self.env.user)
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.invoice', 'Invoice')
    invoice_to_insurer = fields.Boolean('Invoice to Insurance')
    doctor_id = fields.Many2one('podiatry.physician', 'Prescribing Doctor')
    podiatry_appointment_id = fields.Many2one(
        'podiatry.appointment', 'Appointment')
    state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')
    lab_partner_id = fields.Many2one(
        'res.partner', domain=[('is_lab', '=', True)], string='Lab')
    prescription_line_ids = fields.One2many(
        'podiatry.prescription.line', 'name', 'Prescription Line')
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    appointment_id = fields.Many2one('podiatry.appointment')
    is_invoiced = fields.Boolean(copy=False, default=False)
    insurer_id = fields.Many2one('podiatry.insurance', 'Insurer')
    is_shipped = fields.Boolean(default=False, copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'podiatry.prescription.order') or '/'
        return super(podiatry_prescription_order, self).create(vals)

    def prescription_report(self):
        return self.env.ref('pod_app.report_print_prescription').report_action(self)

    @api.onchange('name')
    def onchange_name(self):
        ins_obj = self.env['podiatry.insurance']
        ins_record = ins_obj.search(
            [('podiatry_insurance_partner_id', '=', self.patient_id.patient_id.id)])
        self.insurer_id = ins_record.id or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
