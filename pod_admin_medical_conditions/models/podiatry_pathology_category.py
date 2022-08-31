
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PodiatryPathologyCategory(models.Model):
    _name = 'podiatry.pathology.category'
    _description = 'Podiatry Pathology Category'

    @api.constrains('parent_id')
    def _check_recursion_parent_id(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create a recursive zone.')

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    child_ids = fields.One2many(
        comodel_name='podiatry.pathology.category',
        inverse_name='parent_id',
        string='Children Categories'
    )
    parent_id = fields.Many2one(
        comodel_name='podiatry.pathology.category',
        string='Parent Category',
        index=True
    )
