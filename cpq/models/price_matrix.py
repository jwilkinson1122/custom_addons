from odoo import models, fields


class PriceMatrix(models.Model):
    _name = "price.matrix"
    _description = "CPQ Price Matrix"
    _order = "material_id, length_id, color_id, thickness_id"

    material_id = fields.Many2one(
        "product.attribute.value", string="Material", required=True,
        domain="[('attribute_id.name', '=', 'Top Cover Material')]",
    )
    length_id = fields.Many2one(
        "product.attribute.value", string="Length", required=True,
        domain="[('attribute_id.name', '=', 'Top Cover Length')]",
    )
    color_id = fields.Many2one(
        "product.attribute.value", string="Color",
        domain="[('attribute_id.name', '=', 'Top Cover Color')]",
    )
    thickness_id = fields.Many2one(
        "product.attribute.value", string="Thickness",
        domain="[('attribute_id.name', '=', 'Top Cover Thickness')]",
    )

    price_extra = fields.Float(string="Extra Price", required=True)

    def find_applicable_price(self, template_id, selected_ids):
        matrix_line = self.search([
            ('product_tmpl_id', '=', template_id),
            ('ptav_ids', 'subset_of', selected_ids),
        ], limit=1, order="specificity desc")  # Add specificity logic if needed

        return matrix_line.price_total if matrix_line else None
