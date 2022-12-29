from odoo import models, fields, api, _


class CreatePatient(models.TransientModel):
    _name = 'create.patient'
    _description = 'Create Pet Wizard'
    # patient_id = fields.Many2one('clinic.patient', string="Patient")
    patient_id = fields.Many2one('clinic.patient', string="Patient")
    doctor_id = fields.Many2one(
        'clinic.doctor', string="Doctor", required=True)
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)

    def create_patient(self):
        vals = {
            'doctor_id': self.doctor_id.id,
            'name': self.name,
            'gender': self.gender
        }
        new_patient = self.env['clinic.patient'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'clinic.patient',
                'res_id': new_patient.id,
                'context': context
                }
