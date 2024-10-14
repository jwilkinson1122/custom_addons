from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ProductMatrixWiz(models.TransientModel):
    _name = 'product.matrix.wiz'
    _description = 'Product Matrix'
    _rec_name = "name"

    name = fields.Char("Name", default='Name')
    laterality = fields.Selection([
        ('laterality_lt', 'Left Only'),
        ('laterality_rt', 'Right Only'),
        ('laterality_bl', 'Bilateral')
    ], string="Laterality", required=True, default='laterality_bl')
    matrix_lines = fields.One2many("product.matrix.wiz.line", 'wizard_id', "Lines")
    product_tmpl_id = fields.Many2one("product.template", domain="['|',('is_clothing_size','=',True),('is_textile_size','=',True)]")

    @api.onchange('product_tmpl_id', 'laterality')
    def assign_product_variant_lines(self):
        if not self.product_tmpl_id:
            return

        product_data = [(5, 0)]  # Remove any existing lines before adding new ones

        # Get textile and clothing attributes separately
        textile_attributes = self.product_tmpl_id.attribute_line_ids.filtered(
            lambda l: l.attribute_id.is_textile_size
        )
        clothing_attributes = self.product_tmpl_id.attribute_line_ids.filtered(
            lambda l: l.attribute_id.is_clothing_size
        )

        # Case 1: Product has variants
        if self.product_tmpl_id.product_variant_count > 1:
            products = self.env['product.product'].search([
                ('product_tmpl_id', '=', self.product_tmpl_id.id)
            ])
            for product in products:
                price = product.lst_price
                if self.laterality == 'laterality_bl':
                    price *= 2  # Double the price for bilateral

                product_data.append((0, 0, {
                    'wizard_id': self.id,
                    'name': product.display_name,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'product_id': product.id,
                    'list_price': price,
                    'uom_id': product.uom_id.id,
                    'quantity': 1,
                    'attribute_type': 'variant'
                }))
        else:
            # Case 2: Product has no variants, but attributes are defined
            attribute_lines = self.product_tmpl_id.attribute_line_ids
            for attribute_line in attribute_lines:
                for value in attribute_line.value_ids:
                    attribute_type = 'textile' if attribute_line.attribute_id.is_textile_size else 'clothing'
                    price = self.product_tmpl_id.list_price
                    if self.laterality == 'laterality_bl':
                        price *= 2  # Double the price for bilateral

                    product_data.append((0, 0, {
                        'wizard_id': self.id,
                        'name': f"{self.product_tmpl_id.display_name} - {value.name} ({self.laterality})",
                        'product_tmpl_id': self.product_tmpl_id.id,
                        'product_id': False,  # No variant, use attribute values
                        'attribute_value_id': value.id,
                        'list_price': price,
                        'uom_id': self.product_tmpl_id.uom_id.id,
                        'quantity': 1,
                        'attribute_type': attribute_type
                    }))

                # Add a separator after each attribute type
                separator_label = f"--- {attribute_line.attribute_id.name} End ---"
                product_data.append((0, 0, {
                    'wizard_id': self.id,
                    'name': separator_label,
                    'attribute_type': 'separator'
                }))

        self.matrix_lines = product_data

    def add_variants(self):
        sale_obj = self.env['sale.order'].browse(self._context.get('active_id'))
        if not any(rec.active_bool for rec in self.matrix_lines):
            raise UserError('Please Select At least One Variant or Product')

        for rec in self.matrix_lines:
            if rec.active_bool and rec.attribute_type != 'separator':
                sale_order_line = self.env['sale.order.line']
                sale_order_line.create({
                    'order_id': sale_obj.id,
                    'product_template_id': rec.product_tmpl_id.id,
                    'product_id': rec.product_id.id if rec.product_id else False,
                    'name': rec.name,
                    'product_uom_qty': rec.quantity,
                    'product_uom': rec.uom_id.id,
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
    product_id = fields.Many2one("product.product", "Product Variant", required=False)
    attribute_value_id = fields.Many2one("product.attribute.value", "Attribute Value", required=False)
    list_price = fields.Float("Price")
    quantity = fields.Float("Quantity")
    uom_id = fields.Many2one("uom.uom")
    attribute_type = fields.Selection([
        ('textile', 'Textile'),
        ('clothing', 'Clothing'),
        ('variant', 'Variant'),
        ('separator', 'Separator'),
    ], string="Attribute Type")
    laterality = fields.Selection([
        ('laterality_lt', 'Left Only'),
        ('laterality_rt', 'Right Only'),
        ('laterality_bl', 'Bilateral')
    ], string="Laterality", readonly=True)

# class ProductMatrixWiz(models.TransientModel):
#     _name = 'product.matrix.wiz'
#     _description = 'Product Matrix'
#     _rec_name = "name"

#     name = fields.Char("Name", default='Name')
#     matrix_lines = fields.One2many("product.matrix.wiz.line", 'wizard_id', "Lines")
#     product_tmpl_id = fields.Many2one("product.template",
# domain="['|',('is_clothing_size','=',True),('is_textile_size','=',True)]")

#     @api.onchange('product_tmpl_id')
#     def assign_product_variant_lines(self):
#         if not self.product_tmpl_id:
#             return

#         product_data = [(5, 0)]
#         if self.product_tmpl_id.product_variant_count > 1:
#             # Product has variants
#             products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)])
#             for product in products:
#                 product_data.append((0, 0, {
#                     'wizard_id': self.id,
#                     'name': product.display_name,
#                     'product_tmpl_id': product.product_tmpl_id.id,
#                     'product_id': product.id,
#                     'list_price': product.lst_price,
#                     'uom_id': product.uom_id.id,
#                     'quantity': 1,
#                 }))
#         else:
#             # Product has no variants, use attribute values as selectable options
#             attribute_lines = self.product_tmpl_id.attribute_line_ids
#             for attribute_line in attribute_lines:
#                 for value in attribute_line.value_ids:
#                     product_data.append((0, 0, {
#                         'wizard_id': self.id,
#                         'name': f"{self.product_tmpl_id.display_name} - {value.name}",
#                         'product_tmpl_id': self.product_tmpl_id.id,
#                         'product_id': False,  # No variant, use attribute values
#                         'attribute_value_id': value.id,
#                         'list_price': self.product_tmpl_id.list_price,
#                         'uom_id': self.product_tmpl_id.uom_id.id,
#                         'quantity': 1,
#                     }))

#         self.matrix_lines = product_data

#     def add_variants(self):
#         sale_obj = self.env['sale.order'].browse(self._context.get('active_id'))
#         if not any(rec.active_bool for rec in self.matrix_lines):
#             raise UserError('Please Select At least One Variant or Product')

#         for rec in self.matrix_lines:
#             if rec.active_bool:
#                 sale_order_line = self.env['sale.order.line']
#                 sale_order_line.create({
#                     'order_id': sale_obj.id,
#                     'product_template_id': rec.product_tmpl_id.id,
#                     'product_id': rec.product_id.id if rec.product_id else False,
#                     'name': rec.name,
#                     'product_uom_qty': rec.quantity,
#                     'product_uom': rec.uom_id.id,
#                     'price_unit': rec.list_price,
#                 })
#                 rec.active_bool = False


# class ProductMatrixWizLine(models.TransientModel):
#     _name = 'product.matrix.wiz.line'
#     _description = 'Product Matrix'
#     _rec_name = "name"

#     name = fields.Char("Name", default='Name')
#     active_bool = fields.Boolean('Select')
#     wizard_id = fields.Many2one("product.matrix.wiz")
#     product_tmpl_id = fields.Many2one("product.template", "Product")
#     product_id = fields.Many2one("product.product", "Product Variant", required=False)
#     attribute_value_id = fields.Many2one("product.attribute.value", "Attribute Value", required=False)
#     list_price = fields.Float("Price")
#     quantity = fields.Float("Quantity")
#     uom_id = fields.Many2one("uom.uom")


