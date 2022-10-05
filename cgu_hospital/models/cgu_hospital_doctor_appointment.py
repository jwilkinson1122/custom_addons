from odoo import models, fields, api


class CGUHospitalDoctorAppointment(models.Model):
    _name = 'cgu_hospital.doctor.appointment'
    _description = 'Doctor Appointment'

    name = fields.Char()
    # readonly = True
    active = fields.Boolean(default=True)

    color = fields.Integer()

    date = fields.Date()
    time = fields.Datetime()

    doctor_id = fields.Many2one(
        comodel_name='cgu_hospital.doctor',
        string='Doctor')

    patient_id = fields.Many2one(
        comodel_name='cgu_hospital.patient',
        string='Patient')

    description = fields.Text(string='Description')

    # # діагноз
    # diagnosis_id = fields.Many2one(
    #     comodel_name='hr_hospital.diagnosis',
    #     string='diagnosis')
    #
    #
    # research_ids = fields.Many2many(
    #     string="Researchs",
    #     relation="visit_to_doctor_and_research",
    #     comodel_name='hr_hospital.research',
    #     column1='visit_to_doctor_id',
    #     column2='research_id'
    # )

    @api.onchange('patient_id', 'doctor_id', 'date')
    def _onchange_name(self):
        self.name = f'{self.patient_id.name} | {self.doctor_id.name} ({self.date})'
