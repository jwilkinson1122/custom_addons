from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProductSecondaryUnit(models.Model):
    _name = "product.secondary.unit"
    _description = "Secondary Unit of Measure"

    name = fields.Char(required=True)
    uom_id = fields.Many2one("uom.uom", required=True)

    # Link EITHER to template OR to a specific variant, but not both
    product_tmpl_id = fields.Many2one("product.template", ondelete="cascade")
    product_id = fields.Many2one("product.product", ondelete="cascade")

    _sql_constraints = [
        (
            "tmpl_xor_product",
            "CHECK( (product_tmpl_id IS NOT NULL AND product_id IS NULL) OR "
            "       (product_tmpl_id IS NULL AND product_id IS NOT NULL) )",
            "A secondary unit must be linked either to a product template or to a variant, not both."
        ),
    ]
