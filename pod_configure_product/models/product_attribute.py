from odoo import fields, models


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    prescriptions_order_line_id = fields.Many2one(
        "prescriptions.order.line",
        string="Prescription Order Line",
        required=True,
        ondelete="cascade",
    )
