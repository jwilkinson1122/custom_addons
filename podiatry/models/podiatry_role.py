# -*- coding: utf-8 -*-
 
from odoo import models, fields


class PodiatryRole(models.Model):
    _name = 'podiatry.role'
    _description = 'Practitioner Roles'

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
