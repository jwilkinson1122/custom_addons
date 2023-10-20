# -*- coding: utf-8 -*-

from random import randint

from odoo import fields, models


class PractitionerCategory(models.Model):

    _name = "pod.practitioner.category"
    _description = "Practitioner Category"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    practitioner_ids = fields.Many2many('pod.practitioner', 'practitioner_category_rel', 'category_id', 'emp_id', string='Practitioners')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
