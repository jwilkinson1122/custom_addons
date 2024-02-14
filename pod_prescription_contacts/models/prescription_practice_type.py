# -*- coding: utf-8 -*-
 
from odoo import models, fields


class PrescriptionPracticeType(models.Model):
    _name = 'prescription.practice.type'
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
