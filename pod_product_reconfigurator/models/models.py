# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleProductReConfigurator(models.TransientModel):
    _inherit = 'sale.product.configurator'

    product_id = fields.Many2one('product.product')
    order_line_id = fields.Many2one('sale.order.line')
    order_id = fields.Many2one('sale.order')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def open_product_configurator(self):
        form_view = self.env.ref('pod_product_reconfigurator.sale_product_reconfigurator_view_form')
        return {
            'name': _('Configure a product'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.product.configurator',
            'views': [[form_view.id, 'form']],
            'target': 'new',
            'context': {
                'default_product_template_id': self.product_id.product_tmpl_id.id,
                'default_product_id': self.product_id.id,
                'default_order_line_id': self.id,
                'default_order_id': self.order_id.id
            }
        }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def update_order_line(self, order_line_id, params):
        product_id = params['product_id']
        qty = params['quantity']
        Orderline = self.env['sale.order.line']
        old_order_line = self.env['sale.order.line'].browse(order_line_id)
        variant_attribute_values = params['no_variant_attribute_values']
        product_custom_attribute_values = params['product_custom_attribute_values']
        custom_attribute_ids = self.env['product.attribute.custom.value']
        if product_custom_attribute_values:
            for custom_attribut in product_custom_attribute_values:
                custom_attribute_ids += self.env['product.attribute.custom.value'].new({
                    'custom_value': custom_attribut['custom_value'],
                    'attribute_value_id': custom_attribut['attribute_value_id'],
                    'attribute_value_name': custom_attribut['attribute_value_name']
                })
        defualt_values = Orderline.default_get(Orderline._fields.keys())
        new_order_line = Orderline.new(dict(defualt_values,
            product_id=product_id,
            product_uom_qty=qty,
            order_id=self,
            sequence=old_order_line.sequence,
            product_custom_attribute_value_ids=custom_attribute_ids,
            product_no_variant_attribute_value_ids=list(map(lambda x: int(x['value']), variant_attribute_values)),
        ))
        new_order_line.product_id_change()
        new_order_line.sequence = old_order_line.sequence

        self.order_line += new_order_line
        self.order_line -= old_order_line
