# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class MedicalSpecialty(models.Model):
    _name = 'medical.specialty'
    _description = 'Medical Specialties'

    code = fields.Char(
        string='ID',
        help='Speciality Code',
        size=256,
    )
    name = fields.Char(
        string='Specialty',
        help='Name of the specialty',
        size=256,
        required=True,
        translate=True,
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
