# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class pos_create_sales_order(models.Model):
    _name = 'pos.create.sales.order'
    _description = "POS Create Sale Order"

    def create_sales_order(self, partner_id, orderlines, cashier_id,terms,state,session_id):
        sale_object = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        order_details=[]
        if state == "confirm":
            order_id = sale_object.create({'partner_id': partner_id, 'user_id': cashier_id,'note': terms,'pos_session_id':session_id,'create_from_pos':True})
            for dict_line in orderlines:
                product_obj = self.env['product.product']
                product_dict = dict_line.get('product')

                product_tax = product_obj.browse(product_dict.get('id'))
                tax_ids = []
                for tax in product_tax.taxes_id:
                    tax_ids.append(tax.id)

                product_name = product_obj.browse(product_dict.get('id')).name
                vals = {'product_id': product_dict.get('id'),
                        'name': product_name,
                        'product_uom_qty': product_dict.get('quantity'),
                        'price_unit': product_dict.get('price'),
                        'product_uom': product_dict.get('uom_id'),
                        'tax_id': [(6, 0, tax_ids)],
                        'discount': product_dict.get('discount'),
                        'order_id': order_id.id}
                sale_order_line_obj.create(vals)
            order_id.action_confirm()
            order_details.append(order_id.id)
            order_details.append(order_id.name)
            
        else:
            order_id = sale_object.create({'partner_id': partner_id, 'user_id': cashier_id,'note': terms,'pos_session_id':session_id,'create_from_pos':True})
            for dict_line in orderlines:
                product_obj = self.env['product.product']
                product_dict = dict_line.get('product')

                product_tax = product_obj.browse(product_dict.get('id'))
                tax_ids = []
                for tax in product_tax.taxes_id:
                    tax_ids.append(tax.id)

                product_name = product_obj.browse(product_dict.get('id')).name
                vals = {'product_id': product_dict.get('id'),
                        'name': product_name,
                        'product_uom_qty': product_dict.get('quantity'),
                        'price_unit': product_dict.get('price'),
                        'product_uom': product_dict.get('uom_id'),
                        'tax_id': [(6, 0, tax_ids)],
                        'discount': product_dict.get('discount'),
                        'order_id': order_id.id}
                sale_order_line_obj.create(vals)
            order_details.append(order_id.id)
            order_details.append(order_id.name)
        return order_details

class pos_config(models.Model):
    _inherit = 'pos.config'
    
    create_sale_order = fields.Boolean('Create Sale Order')
    
class POSSession(models.Model):
    _inherit = 'pos.session'
    
    sale_order_ids = fields.One2many('sale.order', 'pos_session_id',  string='Sale Orders')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count')
    

    def _compute_sale_order_count(self):
        for order in self:
            order_ids = self.env['sale.order'].search([('pos_session_id','=',order.id)])
            order.sale_order_count = len(order_ids)
            
            
    def action_view_sale_order(self):
        return {
            'name': _('Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('pos_session_id', 'in', self.ids)],
        }
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    pos_session_id = fields.Many2one('pos.session', string='Session',readonly=True)
    create_from_pos = fields.Boolean('Create From POS',readonly=True)