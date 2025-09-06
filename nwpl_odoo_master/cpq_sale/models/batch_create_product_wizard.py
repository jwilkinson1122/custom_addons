import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BatchCreateProductWizard(models.TransientModel):
    _name = "batch.create.product.wizard"
    _description = "Batch Create Products from Custom Configurations"

    sale_order_line_ids = fields.Many2many(
        "sale.order.line",
        string="Sale Order Lines",
        required=True,
        domain="[('cpq_configuration_json', '!=', False), ('product_id', '=', False)]",
    )

    def action_batch_create(self):
        self.ensure_one()
        created_products = []

        for line in self.sale_order_line_ids:
            product = line.action_create_product_from_configuration()
            if isinstance(product, dict):
                created_products.append(product.get('res_id'))

        if not created_products:
            raise UserError("No products were created. Please check the selected lines.")

        return {
            'type': 'ir.actions.act_window',
            'name': _("Created Products"),
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'domain': [('id', 'in', created_products)],
            'target': 'current',
        }
