# Copyright 2015 LasLabs Dave Lasley <dave@laslabs.com>
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models


class MedicalMedicamentAttributeColor(models.Model):
    _name = 'medical.medicament.attribute.color'
    _description = 'Medical Medicament Physical Attributes - Color'
    _inherit = 'medical.medicament.attribute.abstract'
