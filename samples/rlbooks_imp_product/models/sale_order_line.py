from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLineInherit(models.Model):    
    _inherit = 'sale.order.line'

    has_followproducts = fields.Boolean(string='Has followproducts', default=False,readonly=True,store=True, copy=False)
    followproduct_of_order_line_id = fields.Many2one("sale.order.line", string='Follows order line', ondelete='set null', required=False,store=True,readonly=True, copy=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    followproduct_qty_of_main_product = fields.Integer(default=0, string="Qty in realation to main follow product", readonly=True, store=True, required=False, copy=False)

    def create(self, vals_list):
        
        res = super(SaleOrderLineInherit, self).create(vals_list)
        
        if len(res) == 1:
              
            product_template_id = False
            product_uom_qty = 0
            order_id = False
            sequence = 0

            for values in vals_list:

                if values.get('product_template_id', False) != False:

                    product_template_id = values.get('product_template_id', False)

                if values.get('product_uom_qty', False) != False:

                    product_uom_qty = values.get('product_uom_qty', False)

                if values.get('order_id', False) != False:

                    order_id = values.get('order_id', False)

                if values.get('sequence', False) != False:

                    sequence = values.get('sequence', False)
                    

            if product_template_id != False:

                product_template = self.env['product.template'].browse(product_template_id)

                if product_template.followproduct_ids.ids != False:

                    res.update({

                        'has_followproducts': True

                    })


                    for product in product_template.followproduct_ids:

                        if product.follow_product_id.description_sale != False and product.follow_product_id.description_sale != "":

                            name = '\n'.join([product.follow_product_id.display_name, product.follow_product_id.description_sale])

                        else:
                            
                            name = product.follow_product_id.display_name

                        sequence += 1

                        if product.included_in_price == True:

                            self.env['sale.order.line'].create({

                                'product_id': product.follow_product_id.id,
                                'price_unit': 0,
                                'product_uom_qty': product_uom_qty * product.qty,
                                'name': name,
                                'followproduct_of_order_line_id': res.id,
                                'order_id': order_id,
                                'sequence': sequence,
                                'followproduct_qty_of_main_product': product.qty

                            })    

                        else:
                            
                            self.env['sale.order.line'].create({

                                'product_id': product.follow_product_id.id,
                                'product_uom_qty': product_uom_qty * product.qty,
                                'name': name,
                                'followproduct_of_order_line_id': res.id,
                                'order_id': order_id,
                                'sequence': sequence,
                                'followproduct_qty_of_main_product': product.qty

                            })   
        
      
        return res

    def write(self, values):

        old_qty = self.product_uom_qty

        res = super(SaleOrderLineInherit, self).write(values)
        
        if self.has_followproducts == True and self.state == 'draft':

            follow_products = self.env['sale.order.line'].search([['followproduct_of_order_line_id','=',self.id]])

            for follow_product in follow_products:

                follow_product.update({
                    'product_uom_qty': follow_product.product_uom_qty + (self.product_uom_qty - old_qty) * follow_product.followproduct_qty_of_main_product,
                    'price_unit': follow_product.price_unit,
                })

        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):

        if self.state != 'draft':

            old_price = self.price_unit

            super(SaleOrderLineInherit, self).product_uom_change()

            self.update({
                'price_unit': old_price,
            })

        else:

            super(SaleOrderLineInherit, self).product_uom_change()

