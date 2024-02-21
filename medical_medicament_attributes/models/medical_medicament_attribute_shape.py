# Copyright 2015 LasLabs Dave Lasley <dave@laslabs.com>
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models


class MedicalMedicamentAttributeShape(models.Model):
    _name = 'medical.medicament.attribute.shape'
    _description = 'Medical Medicament Physical Attributes - Shape'
    _inherit = 'medical.medicament.attribute.abstract'
