from odoo import fields, models, api


class SaleOrderLineWizard(models.TransientModel):
    _name = 'sale.order.line.wizard'

    wizard_id = fields.Many2one('version.wizard', string="Wizard")
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char(string="Description")
    product_uom_qty = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Unit Price")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price
