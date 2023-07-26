from odoo import models, fields, api
from datetime import datetime


class Appointment(models.Model):
    _name = 'eclinic.appointment'
    _description = 'Information about appointments'

    name = fields.Char(string='Name', required=True)
    clinic_id = fields.Many2one('clinic', string='Location')
    patient_id = fields.Many2one('eclinic.patient', string='Patient')
    doctor_id = fields.Many2one('eclinic.doctor', string='Doctor')
    appointment_date = fields.Date(string='Appointment Date', default=fields.Date.today())
    consultation_notes = fields.Text(string='Consultation Notes')
    prescription_notes = fields.Text(string='Prescription Notes')
    
    billing_amount = fields.Float(string='Billing Amount')
    payment_amount = fields.Float(string='Payment Amount')
    payment_date = fields.Date(string='Payment Date')

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            today = datetime.now().strftime("%Y%m%d")
            self.name = 'APPOINTMENT/' + self.patient_id.name + '/' + today

    def open_create_appointment_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Appointment',
            'res_model': 'eclinic.appointment',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_clinic_id': self.clinic_id.id,
            },
        }

    def open_schedule_appointment_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Schedule Appointment',
            'res_model': 'eclinic.appointment',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_clinic_id': self.clinic_id.id,
            },
        }

    def open_appointment_calendar(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment Calendar',
            'res_model': 'eclinic.appointment',
            'view_mode': 'calendar,tree',
            'target': 'current',
        }

    def open_billing(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Billing',
            'res_model': 'eclinic.appointment',
            'view_mode': 'form',
            'target': 'current',
        }

    def open_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'res_model': 'eclinic.appointment',
            'view_mode': 'form',
            'target': 'current',
        }