# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class MedicalDrugRoute(models.Model):
    _name = 'medical.drug.route'
    _description = 'Medical Drug Route'

    name = fields.Char(
        required=True,
        translate=True,
    )
    code = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Drug route name must be unique!'),
        ('code_uniq', 'UNIQUE(code)', 'Drug route code must be unique!')
    ]
