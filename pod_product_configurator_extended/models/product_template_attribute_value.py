from odoo import models, api


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    @api.model
    def get_closest_value_for_product(self, xml_id, current_value, product_tmpl_id):
        product_attribute = self.env.ref(xml_id)
        product = self.env["product.template"].browse(product_tmpl_id)
        related_lines = product.attribute_line_ids.filtered(lambda x: x.attribute_id == product_attribute)
        possible_values = related_lines.value_ids.sorted(lambda x: int(x.name))

        closet_upper_value = self.env["product.attribute.value"]
        is_exact_match = False
        for value in possible_values:
            if current_value <= int(value.name):
                closet_upper_value = value
                if int(closet_upper_value.name) == current_value:
                    is_exact_match = True
                break
        product_template_attribute_value = self.env["product.template.attribute.value"].search([
            ("attribute_line_id", "=", related_lines.id),
            ("product_tmpl_id", "=", product_tmpl_id),
            ("product_attribute_value_id", "=", closet_upper_value.id),
        ])
        return product_template_attribute_value.id, is_exact_match
