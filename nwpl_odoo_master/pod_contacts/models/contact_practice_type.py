# -*- coding: utf-8 -*-
 
from odoo import models, fields


class ContactPracticeType(models.Model):
    _name = 'contact.practice.type'
    _description = 'Practice Types'

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
