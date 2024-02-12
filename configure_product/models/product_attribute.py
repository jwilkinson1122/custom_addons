from odoo import fields, models


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    prescription_line_id = fields.Many2one(
        "prescription.line",
        string="Prescription Order Line",
        required=True,
        ondelete="cascade",
    )
