from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_booking = fields.Boolean(string='Is Booking', default=False)

    @api.model
    def create(self, vals):
        if vals.get('is_booking'):
            sequence_code = 'sale.order.line'
        else:
            sequence_code = 'sale.order'
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or _('New')
        res = super(SaleOrder, self).create(vals)
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_booking = fields.Float(string='Quantity Booking', default=1.0, store=True)
    product_template_id = fields.Many2one('product.template', string='Product Template', compute='_compute_product_template_id')

    @api.onchange('product_uom_qty')
    def _onchange_qty_booking(self):
        for line in self:
            line.qty_booking = line.product_uom_qty

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for record in self:
            record.product_template_id = record.product_id.product_tmpl_id

    @api.onchange('order_id.is_booking', 'price_unit', 'product_id')
    def _onchange_is_booking(self):
        for line in self:
            if line.product_id:
                price = line.product_id.lst_price
                if line.order_id.is_booking:
                    line.price_unit = price * 1.1
                else:
                    line.price_unit = price

