# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Sample(models.Model):
    _name = "sh.lab.test.sample.type"
    _description = "Sample Information"

    name = fields.Char(string="Name")
