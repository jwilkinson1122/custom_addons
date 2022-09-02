

from odoo import models, fields


class PodSpecialty(models.Model):
    _name = 'pod.specialty'
    _description = 'Medical Specialty'
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Code must be unique!'),
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]

    code = fields.Char(
        string='Code',
        help='Speciality code',
        size=256,
        required=True,
    )
    name = fields.Char(
        string='Name',
        help='Name of the specialty',
        size=256,
        required=True,
    )
    category = fields.Selection(
        [
            ('clinical', 'Clinical specialties'),
            ('surgical', 'Surgical specialties'),
            ('medical', 'Medical-surgical specialties'),
            ('diagnostic', 'Practiceoratory or diagnostic specialties'),
        ],
        'Category of specialty'
    )
