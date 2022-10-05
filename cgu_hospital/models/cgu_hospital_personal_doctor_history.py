from odoo import models, fields, api


class CGUHospitalDoctorHistory(models.Model):
    _name = 'cgu_hospital.personal.doctor.history'
    _description = 'HR Hospital personal_doctor_history'

    name = fields.Char()
    active = fields.Boolean(default=True)

    # дату діагностування(date     of     diagnosis)
    date = fields.Date()

    # лікарь(doctor)
    doctor_id = fields.Many2one(
        comodel_name='cgu_hospital.doctor',
        string='Doctor')

    # patient
    patient_id = fields.Many2one(
        comodel_name='cgu_hospital.patient',
        string='patient')

    @api.onchange('patient_id', 'doctor_id', 'doctor_id', 'date')
    def _onchange_name(self):
        self.name = f'{self.patient_id.name} | {self.doctor_id.name} ({self.date})'
