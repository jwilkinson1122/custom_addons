# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class om_hospital(models.Model):
#     _name = 'om_hospital.om_hospital'
#     _description = 'om_hospital.om_hospital'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HospitalAppointment(models.Model):
    _name = 'syn.hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Syn Hospital Appointment'
    _rec_name = 'ref'
    
    patient_id = fields.Many2one("syn.hospital.patient",string="Patient Name", ondelete="restrict")
    gender = fields.Selection(related="patient_id.gender",readonly=False)
    appointment_time = fields.Datetime(string="Appointment Time",default=fields.Datetime.now)
    booking_date = fields.Date(string="Booking Date",default=fields.Date.context_today)
    ref = fields.Char(string="Reference")
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([
        ('0','Normal'),
        ('1','Low'),
        ('2','High'),
        ('3','Very High')
        ], string="Priority")
    state = fields.Selection([
        ('draft','Draft'),
        ('in_consultation','In Consultation'),
        ('done','Done'),
        ('cancel','Cancelled')
        ], string="Status", default="draft")
    doctor_id = fields.Many2one('res.users', string='Doctor')
    pharmacy_line_ids = fields.One2many('syn.hospital.medicine','appointment_id',string="Pharmacy Lines")
    nures_ids = fields.Many2many('res.users',string="Nurse")
    reason_cancel = fields.Char(string="Reason For Cancel")

    @api.model
    def create(self,vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('syn.hospital.appointment')
        return super(HospitalAppointment,self).create(vals)

    def unlink(self):
        if self.state == 'done':
            raise ValidationError(_('You can not delete appointment with status done !'))
        return super(HospitalAppointment,self).unlink()


    # @api.onchange('patient_id')
    # def onchange_patient_id(self):
    #     self.ref = self.patient_id.ref

    def action_test(self):
        for rec in self:
            rec.state = "cancel"
        return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Appointment Cancelled',
                    'type': 'rainbow_man',
                }
            }

    def action_in_consulation(self):
        for rec in self:
            rec.state='in_consultation';

    def action_done(self):
        for rec in self:
            rec.state='done';

    def action_cancel(self):
        for rec in self:
            rec.state='cancel';

    def action_draft(self):
        for rec in self:
            rec.state='draft';