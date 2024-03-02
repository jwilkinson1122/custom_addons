# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionTypeModelCategory(models.Model):
    _name = 'prescription.type.model.category'
    _description = 'Category of the model'
    _order = 'sequence asc, id asc'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Category name must be unique')
    ]

    name = fields.Char(required=True)
    sequence = fields.Integer()
