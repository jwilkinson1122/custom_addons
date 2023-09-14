

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"

    category_product_id = fields.Many2one(
        "product.product", domain=[("type", "=", "service")]
    )

    @api.constrains("category_product_id")
    def _check_category_product(self):
        for rec in self.filtered(lambda r: r.category_product_id):
            if rec.category_product_id.type != "service":
                raise ValidationError(_("Category product must be always a service"))
