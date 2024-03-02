# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionTypeState(models.Model):
    _name = 'prescription.type.state'
    _order = 'sequence asc'
    _description = 'Prescription Status'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()

    _sql_constraints = [('prescription_state_name_unique', 'unique(name)', 'State name already exists')]
