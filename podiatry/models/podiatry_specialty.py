from odoo import models, fields


class Specialty(models.Model):
    _name = 'podiatry.specialty'
    _description = 'Medial Specialty'
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Code must be unique!'),
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]

    # name = fields.Char()

    name = fields.Char(
        string='Name',
        help='Name of the specialty',
        size=256,
        required=True,
    )
    
    code = fields.Char(
        string='Code',
        help='Specialty code',
        size=256,
        required=True,
    )

    active = fields.Boolean(default=True)

    parent_id = fields.Many2one(
        comodel_name='podiatry.specialty',
        string='Parent Category',
        index=True,
        ondelete='cascade')
