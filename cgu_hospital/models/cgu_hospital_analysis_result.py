from odoo import models, fields


class CGUHospitalAnalysisResalt(models.Model):
    _name = 'cgu_hospital.analysis.result'
    _description = 'Analysis Resalt'

    date = fields.Date()

    name = fields.Char()
    active = fields.Boolean(default=True)

    analysis_direction_id = fields.Many2one(
        comodel_name='cgu_hospital.analysis.direction',
        string='Analysis Direction')

    resalt = fields.Text()

    doctor_id = fields.Many2one(
        comodel_name='cgu_hospital.doctor',
        string='Doctor')

    patient_id = fields.Many2one(
        comodel_name='cgu_hospital.patient',
        string='patient')

    analysis_type_id = fields.Many2one(
        comodel_name='cgu_hospital.analysis.type',
        string='analysis.type')
