from odoo import fields, models, api


class SaleOrderLineVersion(models.Model):
    _name = "sale.order.line.version"
    _description = "Sale Order Line Version"

    order_version_id = fields.Many2one('sale.order.version', string="Order Version")
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Text(string="Description")
    product_uom_qty = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Unit Price")

    subtotal = fields.Monetary(string="Subtotal", compute='_compute_subtotal', store=True)
    currency_id = fields.Many2one(related='order_version_id.currency_id', depends=['order_version_id.currency_id'],
                                  store=True, string='Currency')

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_uom_qty * line.price_unit
