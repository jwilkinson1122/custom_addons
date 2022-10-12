from odoo import models, fields


class CGUHospitalSpecialty(models.Model):
    _name = 'cgu_hospital.speciality'
    _description = 'speciality'

    name = fields.Char()

    active = fields.Boolean(default=True)

    parent_id = fields.Many2one(
        comodel_name='cgu_hospital.speciality',
        string='Parent Category',
        index=True,
        ondelete='cascade')
