# -*- coding: utf-8 -*-
 
from odoo import models, fields


class PodiatryAccountType(models.Model):
    _name = 'podiatry.practice.type'
    _description = 'Account Types'

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
