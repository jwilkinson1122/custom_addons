from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_product_description(self):
        """Modify description to include laterality"""
        for line in self:
            description = line.product_id.display_name
            laterality_value = line.product_id.attribute_value_ids.filtered(
                lambda v: v.attribute_id.name == 'Laterality'
            )
            if laterality_value:
                description += ' (' + laterality_value.name + ')'
            line.name = description
            
    def _get_line_description(self, product, product_uom_qty):
        """Generate the product description including laterality information for the sales order line."""
        description = super(SaleOrderLine, self)._get_line_description(product, product_uom_qty)
        
        # Fetch laterality attributes from the product configuration
        laterality_info = []
        for attribute_value in product.product_template_attribute_value_ids:
            if attribute_value.attribute_id.name == 'Laterality' and attribute_value.product_attribute_value_id:
                laterality_info.append(attribute_value.product_attribute_value_id.name)

        if laterality_info:
            description += " - " + ", ".join(laterality_info)
        
        return description
