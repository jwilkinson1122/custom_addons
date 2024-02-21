# Copyright 2008 Luis Falcon <falcon@gnuhealth.org>
# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import fields, models


class MedicalDrugRoute(models.Model):
    _name = 'medical.drug.route'
    _description = 'Medical Drug Route'

    name = fields.Char(
        string='name',
        required=True,
        translate=True
    )
    code = fields.Char(string='code')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Drug Route name must be unique!'),
    ]
