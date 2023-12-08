# -*- coding: utf-8 -*-
 
from odoo import models, fields


class PodiatryPracticeType(models.Model):
    _name = 'pod.practice.type'
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
