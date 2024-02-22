from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    customer_ids = fields.One2many(
        comodel_name="product.customerinfo",
        inverse_name="product_tmpl_id",
        string="Customer",
    )

    variant_customer_ids = fields.One2many(
        comodel_name="product.customerinfo",
        inverse_name="product_tmpl_id",
        string="Variant Customer",
    )
