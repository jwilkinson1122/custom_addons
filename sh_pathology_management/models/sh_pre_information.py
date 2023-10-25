# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Information(models.Model):
    _name = "sh.lab.test.pre.info"
    _description = "Test Information"

    name = fields.Char(string="Name")
