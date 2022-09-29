from odoo import models, fields


class CGUHospitalAnalysisDirection(models.Model):
    _name = 'cgu_hospital.analysis.direction'
    _description = 'Analysis Direction'

    date = fields.Date()

    name = fields.Char()
    active = fields.Boolean(default=True)

    doctor_id = fields.Many2one(
        comodel_name='cgu_hospital.doctor',
        string='Doctor')

    patient_id = fields.Many2one(
        comodel_name='cgu_hospital.patient',
        string='patient')

    analysis_type_id = fields.Many2one(
        comodel_name='cgu_hospital.analysis.type',
        string='analysis.type')

    comment = fields.Text()
