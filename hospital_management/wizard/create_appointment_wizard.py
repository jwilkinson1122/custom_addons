from email.policy import default
from odoo import models, fields, api


class CreateAppointment(models.TransientModel):
    _name = 'create.appointment.wizard'
    _description = 'Create Appointment Wizard'

    patient_id = fields.Many2one('hospital.patient', "Patient")
    doctor_id = fields.Many2one('hospital.doctor', "Doctor")
    date = fields.Date("Date", default=fields.Date.today)
    appointment_time = fields.Datetime("Time", default=fields.Datetime.now)

    @api.model
    def default_get(self, fields_list):

        active_model = self.env.context['active_model']
        active_id = self.env.context['active_id']

        record = self.env[active_model].browse(active_id)

        res = super().default_get(fields_list)
        res.update({
            'patient_id': record.id
        })
        return res

    def create_appointment(self):
        vals = {
            'patient_id' : self.patient_id.id,
            'doctor_id' : self.doctor_id.id,
            'date_appointment' : self.date,
            'date_checkup' : self.appointment_time,
            'company_id':self.env.company.id,
            'partner_id':self.env.user.id,
            'date_order':fields.Datetime.now()
        }
        appointment_obj = self.env['hospital.appointment']
        appointment_obj.with_context(create_mode='wizard').create(vals)

