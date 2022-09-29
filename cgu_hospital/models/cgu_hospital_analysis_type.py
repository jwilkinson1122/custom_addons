from odoo import models, fields


class CGUHospitalAnalysisType(models.Model):
    _name = 'cgu_hospital.analysis.type'
    _description = 'Analysis Type'

    name = fields.Char()

    active = fields.Boolean(default=True)

    parent_id = fields.Many2one(
        comodel_name='cgu_hospital.analysis.type',
        string='Parent Category',
        index=True,
        ondelete='cascade')
