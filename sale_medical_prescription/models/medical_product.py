# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html)

from odoo import fields, models


class MedicalMedicament(models.Model):
    _inherit = 'product.product'

    is_prescription = fields.Boolean(
        string='Prescription Required',
        compute='_compute_is_prescription',
        help='Indicates if a prescription is required for this product',
    )
    is_controlled = fields.Boolean(
        string='Controlled Substance',
        help='Check this if the product is a controlled substance',
    )

    def _compute_is_prescription(self):
        prescription_categ_id = self.env.\
            ref('sale_medical_prescription.product_category_rx')
        for record in self:
            if record.categ_id == prescription_categ_id:
                record.is_prescription = True
                continue
            record.is_prescription = record.categ_id.\
                _is_descendant_of(prescription_categ_id)
