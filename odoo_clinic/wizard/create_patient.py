from odoo import models, fields, api, _


class CreatePatient(models.TransientModel):
    _name = 'create.patient'

    patient_id = fields.Many2one('clinic.patient', string="Patient")

    doctor = fields.Many2one(
        'res.partner.doctor', string="Doctor", required=True)
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)

    def create_patient(self):
        vals = {
            'doctor': self.doctor.id,
            'name': self.name,
            'gender': self.gender
        }
        self.doctor.message_post(
            body="Your New Patient Has Been Added", subject="New Patient")
        new_patient = self.env['res.partner'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'res_id': new_patient.id,
                'context': context
                }
