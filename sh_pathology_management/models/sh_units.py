# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Units(models.Model):
    _name = "sh.lab.test.unit"
    _description = "Units Description"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(default=True)
