# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class MedicalDrugForm(models.Model):
    _name = 'medical.drug.form'
    _description = 'Medical Drug Form'

    name = fields.Char(
        required=True,
        translate=True,
    )
    code = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Code should be unique!'),
    ]
