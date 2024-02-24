from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_description_sale = fields.Text(
        string="Variant Sale Description",
        help="A description of the product variant that you want to "
        "communicate to your customers."
        "This description will be copied to every Sale Order",
        translate=True,
    )

    variant_description_prescription = fields.Text(
        string="Variant Prescription Description",
        help="A description of the product variant that you want to "
        "communicate to your customers."
        "This description will be copied to every Prescription Order",
        translate=True,
    )
