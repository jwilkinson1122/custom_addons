# Copyright 2015 LasLabs Dave Lasley <dave@laslabs.com>
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models


class MedicalMedicamentAttributeFlavor(models.Model):
    _name = 'medical.medicament.attribute.flavor'
    _description = 'Medical Medicament Physical Attributes - Flavor'
    _inherit = 'medical.medicament.attribute.abstract'
