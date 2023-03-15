from odoo import models, fields


class Specialty(models.Model):
    _name = 'podiatry.speciality'
    _description = 'speciality'

    name = fields.Char()

    active = fields.Boolean(default=True)

    parent_id = fields.Many2one(
        comodel_name='podiatry.speciality',
        string='Parent Category',
        index=True,
        ondelete='cascade')
