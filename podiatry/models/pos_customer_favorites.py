# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CustomerFavouriteProduct(models.Model):
    _name = "customer.favorite.product"

    product_id = fields.Many2one('product.product', string='Product')
    product_count = fields.Integer(string='Product Sale', default=0)
    last_update = fields.Datetime(string='Update Date')
    pos_category = fields.Many2one('pos.category', string="Pos Category")
    partner_id = fields.Many2one('res.partner', string="Customer")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_favorites_ids = fields.One2many(
        'customer.favorite.product', 'partner_id', string="Favorite Product")


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, pos_order, draft, existing_order):
        result = super(PosOrder, self)._process_order(
            pos_order, draft, existing_order)
        if pos_order.get('data').get('partner_id'):
            customer_favorites = self.env['customer.favorite.product']
            for line in pos_order['data']['lines']:
                customer_fav_product = customer_favorites.search([('partner_id', '=', pos_order.get(
                    'data').get('partner_id')), ('product_id', '=', line[2]['product_id'])])
                if customer_fav_product:
                    customer_fav_product.product_count = customer_fav_product.product_count + \
                        line[2]['qty']
                else:
                    product = self.env['product.product'].browse(
                        line[2]['product_id'])
                    customer_favorites.create({
                        'partner_id': pos_order.get('data').get('partner_id'),
                        'product_id': line[2]['product_id'],
                        'product_count': line[2]['qty'],
                        'last_update': pos_order['data']['creation_date'].replace('T', ' ')[:19],
                        'pos_category': product.pos_categ_id.id or False,
                    })
        return result
