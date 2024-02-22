from odoo import api, fields, models


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    required = fields.Boolean(
        default=False,
    )

    _sql_constraints = [
        (
            "product_attribute_uniq",
            "unique(product_tmpl_id, attribute_id)",
            "The attribute already exists for this product",
        )
    ]

    @api.onchange("attribute_id")
    def _onchange_attribute_id_clean_value(self):
        """This is for consistency when changing attribute in the product."""
        self.value_ids = False
