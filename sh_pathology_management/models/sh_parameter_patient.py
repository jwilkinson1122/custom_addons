# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Parameter(models.Model):
    _name = "sh.lab.test.parameter.patient"
    _description = "Patient Parameter Description"
    _order = "id desc"

    name = fields.Char(translate=True, string="Name")

    sequence = fields.Integer(string="Sequence")
    min_value = fields.Float(string="Minimum Value")
    max_value = fields.Float(string="Maximum Value")
    normal_value = fields.Float(string="Normal Value")
    unit_id = fields.Many2one(
        'sh.lab.test.unit', ondelete='cascade', string="Unit")
    patient_value = fields.Float(string="Obtained Value")
    description = fields.Html()
    active = fields.Boolean(default=True)
    request_line_id = fields.Many2one(
        'sh.patho.request.line', ondelete='cascade', index=True, copy=True)
