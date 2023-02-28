# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('syn.hospital.appointment',string="Appointment", domain=[('state','=','draft')])
    reason = fields.Text(string="Reason")

    # @api.model
    # def default_get(self,fields):
    #     res = super(CancelAppointmentWizard,self).default_get(fields)
    #     if self.env.context.get('active_id'):
    #         res['appointment_id']=self.env.context.get('active_id')
    #     print("default_get executed")
    #     print(self.env.context)
    #     return res;

    def action_cancel(self):    
        if self.appointment_id.booking_date == fields.Date.today():
            raise ValidationError(_('Sorry , cancellation is not allowed on the same day of booking !'))
        else:
            for rec in self:
                rec.appointment_id.state='cancel'
                rec.appointment_id.reason_cancel=rec.reason
            return