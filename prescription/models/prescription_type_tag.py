# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionTypeTag(models.Model):
    _name = 'prescription.type.tag'
    _description = 'Prescription Tag'

    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color')

    _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists!")]
