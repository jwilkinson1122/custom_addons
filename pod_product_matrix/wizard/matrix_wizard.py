from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductMatrixWiz(models.TransientModel):
    _name = 'product.matrix.wiz'
    _description = 'Product Matrix'
    _rec_name = "name"

    name = fields.Char("Name", default='Name')
    matrix_lines = fields.One2many("product.matrix.wiz.line", 'wizard_id', "Lines")
    product_tmpl_id = fields.Many2one("product.template",
                                      domain="['|',('is_clothing_size','=',True),('is_textile_size','=',True)]")

    @api.onchange('product_tmpl_id')
    def assign_product_variant_lines(self):
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        products = self.env['product.template.attribute.value'].search(domain)
        if self.product_tmpl_id:
            product_data = [(5, 0)]
            for product in products:
                product_data.append((0, 0, {
                    'wizard_id': self.id,
                    'name': product.product_tmpl_id.name + ' ' + product.name,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'product_id': product.ptav_product_variant_ids[0].id,
                    'list_price': product.ptav_product_variant_ids[0].lst_price,
                    'uom_id': product.ptav_product_variant_ids[0].uom_id.id,
                    'quantity': 1,
                }))
            self.matrix_lines = product_data

    def add_variants(self):
        sale_obj = self.env['sale.order'].browse(self._context.get('active_id'))
        if not any(rec.active_bool == True for rec in self.matrix_lines):
            raise UserError('Please Select At least One Variant')
        for rec in self.matrix_lines:
            if rec.active_bool:
                sale_order_line = self.env['sale.order.line']
                sale_order_line.create({
                    'order_id': sale_obj.id,
                    'product_template_id': rec.product_tmpl_id.id,
                    'product_id': rec.product_id.id,
                    'name': rec.name,
                    'product_uom_qty': rec.quantity,
                    'product_uom': rec.product_id.uom_id.id,
                    'price_unit': rec.list_price,
                })
                rec.active_bool = False


class ProductMatrixWizLine(models.TransientModel):
    _name = 'product.matrix.wiz.line'
    _description = 'Product Matrix'
    _rec_name = "name"

    name = fields.Char("Name", default='Name')
    active_bool = fields.Boolean('Select')
    wizard_id = fields.Many2one("product.matrix.wiz")
    product_tmpl_id = fields.Many2one("product.template", "Product")
    product_id = fields.Many2one("product.product", "Product Variant")
    list_price = fields.Float("Price")
    quantity = fields.Float("Quantity")
    uom_id = fields.Many2one("uom.uom")
