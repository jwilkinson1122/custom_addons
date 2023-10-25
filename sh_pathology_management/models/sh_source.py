# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Source(models.Model):
    _name = "sh.patho.source"
    _description = "Source Description"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
