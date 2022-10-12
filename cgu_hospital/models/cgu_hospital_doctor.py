from odoo import models, fields


class CGUHospitalDoctor(models.Model):
    _name = 'cgu_hospital.doctor'
    _inherit = ['cgu_hospital.contact.mixin', ]
    _description = 'Doctor'

    active = fields.Boolean(default=True)
    color = fields.Integer()

    speciality_id = fields.Many2one(
        comodel_name='cgu_hospital.speciality',
        string='speciality')

    personal_patient_ids = fields.One2many(
        comodel_name='cgu_hospital.patient',
        inverse_name='personal_doctor_id',
        string='personal patients')

    doctor_history_ids = fields.One2many(
        comodel_name='cgu_hospital.personal.doctor.history',
        inverse_name='doctor_id',
        string='doctor_history')

    # patient_visit_ids = fields.One2many(
    #     comodel_name='hr_hospital.visit.to.doctor',
    #     inverse_name='doctor_id',
    #     string='patient_visit')
