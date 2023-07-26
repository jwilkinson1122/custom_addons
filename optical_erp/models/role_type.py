# -*- coding: utf-8 -*-
 
from odoo import models, fields


class RoleType(models.Model):
    _name = 'role.type'
    _description = 'Contact Roles'

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
