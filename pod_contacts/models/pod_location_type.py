# -*- coding: utf-8 -*-
 
from odoo import models, fields


class PodiatryLocationType(models.Model):
    _name = 'pod.location.type'
    _description = 'Types'

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
