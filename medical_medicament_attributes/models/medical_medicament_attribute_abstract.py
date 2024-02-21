# Copyright 2015 LasLabs Dave Lasley <dave@laslabs.com>
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import fields, models


class MedicalMedicamentAttributeAbstract(models.AbstractModel):
    _name = 'medical.medicament.attribute.abstract'
    _description = 'Medical Medicament Attributes Abstract'

    name = fields.Char(string="Full Name of Attribute")
    code = fields.Char(string="Short Code of Attribute")
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Attribute code must be unique.'),
        ('name_uniq', 'UNIQUE(name)', 'Attribute name must be unique.'),
    ]
