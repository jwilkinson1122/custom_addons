
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PodiatryPathology(models.Model):
    _name = 'podiatry.pathology'
    _description = 'Podiatry Pathology'

    @api.constrains('code')
    def _check_unicity_name(self):
        domain = [
            ('code', '=', self.code),
        ]
        if len(self.search(domain)) > 1:
            raise ValidationError('"code" Should be unique per Pathology')

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Code',
        required=True
    )
    notes = fields.Text(
        string='Notes',
        translate=True
    )
    protein = fields.Char(
        string='Protein involved'
    )
    chromosome = fields.Char(
        string='Affected Chromosome'
    )
    gene = fields.Char()
    category_id = fields.Many2one(
        comodel_name='podiatry.pathology.category',
        string='Category of Pathology',
        index=True
    )
    podiatry_pathology_group_m2m_ids = fields.Many2many(
        comodel_name='podiatry.pathology.group',
        column1='pathology_id',
        colmun2='pathology_group_id',
        string='Podiatry Pathology Groups',
        relation="pathology_id_pathology_group_id_rel"
    )
