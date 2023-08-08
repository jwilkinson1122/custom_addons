# -*- coding: utf-8 -*-
 
from odoo import models, fields


class PodiatryAddressType(models.Model):
    _name = 'podiatry.address.type'
    _description = 'Address Types'

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
