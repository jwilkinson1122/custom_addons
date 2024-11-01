# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PodiatryMedicine(models.Model):
    """For creating the medicines used in the podiatry clinic"""

    _inherit = "product.template"

    is_medicine = fields.Boolean("Is Medicine", help="If the product is a Medicine")
    generic_name = fields.Char(
        string="Generic Name", help="Generic name of the medicament"
    )
    dosage_strength = fields.Integer(
        string="Dosage Strength", help="Dosage strength of medicament"
    )

    @api.constrains("is_medicine", "dosage_strength")
    def _check_dosage_strength(self):
        for record in self:
            if record.is_medicine and not record.dosage_strength:
                raise ValidationError(
                    _("Dosage Strength must be set for products marked as Medicine.")
                )
