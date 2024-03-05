# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class PrescriptionOrderLine(models.Model):
    _inherit = "prescription.order.line"

    laterality = fields.Selection([
        ('lt_single', 'Left'),
        ('rt_single', 'Right'),
        ('bl_pair', 'Bilateral')
    ], string='Laterality', required=True, default='bl_pair', help="Select which side the product is for.")
    
    is_custom_product = fields.Boolean("Have Custom Options")
    prescription_options_ids = fields.One2many('prescription.custom.options', 'order_line_id', string="Custom Options")
    prescription_options_price = fields.Float(compute='_compute_options_price', string="Options Price", digits='Product Price')
    non_discount_option_price = fields.Float(compute='_compute_non_discount_option_price', string="Non Discount Option Price", digits='Product Price')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    @api.model
    def get_laterality_display(self):
        return dict(self.fields_get(allfields=['laterality'])['laterality']['selection']).get(self.laterality, '')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.is_custom_product = bool(self.product_id.custom_option_ids)

    @api.depends('prescription_options_ids.price')
    def _compute_options_price(self):
        for record in self:
            record.prescription_options_price = sum(record.prescription_options_ids.mapped('price'))

    @api.depends('prescription_options_price', 'discount')
    def _compute_non_discount_option_price(self):
        for record in self:
            # Placeholder for actual calculation if needed
            record.non_discount_option_price = record.prescription_options_price

    @api.depends('price_unit', 'product_uom_qty', 'tax_id')
    def _compute_amount(self):
        for line in self:
            tax_results = line.tax_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_subtotal': tax_results['total_excluded'],
                'price_tax': tax_results['total_included'] - tax_results['total_excluded'],
                'price_total': tax_results['total_included'],
            })

    def configure_product(self):
        return {
            'name': "Configure Product",
            'view_mode': 'form',
            'res_model': 'prescription.order.line',
            'view_id': self.env.ref('pod_product_custom_options.prescription_order_line_custom_options_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def calculate_total_price(self):
        options_price = self._compute_options_price()
        laterality_multiplier = 2 if self.laterality == 'bl_pair' else 1
        self.price_total = (self.price_unit + options_price) * laterality_multiplier

    def save_option(self):
        product_context = self._context.copy()
        product = self.product_id.with_context(product_context)
        self.name = product.display_name
        self.calculate_total_price()

        # Additional logic to handle taxes, discounts, etc.


# class PrescriptionOrderLine(models.Model):
#     _inherit = "prescription.order.line"

#     laterality = fields.Selection([
#         ('lt_single', 'Left'),
#         ('rt_single', 'Right'),
#         ('bl_pair', 'Bilateral')
#     ], string='Laterality', required=True, default='bl_pair', help="Select which side the product is for.")

#     is_custom_product = fields.Boolean("Have custom options")

#     option_selections = fields.One2many(
#         'option.selection.entry', 'wizard_id', string="Option Selections"
#     )
#     prescription_options_ids = fields.One2many(
#         'prescription.custom.options', 'order_line_id',string="Custom Options")
#     prescription_options_price = fields.Float(string="Price",
#         compute='_compute_options_price',
#         digits=dp.get_precision('Product Price'),
#         help="Price for the custom option.")
#     non_discount_option_price = fields.Float(string="Non Discount Option Price",
#         digits=dp.get_precision('Product Price'),
#         help="Price for the non discount with custom options product price.")
    
#     price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
#     price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
#     price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

#     def get_laterality_display(self):
#         """
#         Returns the display value of the laterality field.
#         """
#         laterality_display_values = dict(self._fields['laterality'].selection)
#         return laterality_display_values.get(self.laterality, '')

#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         if self.product_id.custom_option_ids:
#             self.is_custom_product = True
#         else:
#             self.is_custom_product = False

#     @api.depends('prescription_options_ids.price')
#     def _compute_options_price(self):
#         for line in self:
#             line.prescription_options_price = sum(line.prescription_options_ids.mapped('price'))

#     def configure_product(self):
#         productObj = self.product_id
#         if productObj.custom_option_ids:
#             return {
#                 'name': ("Information"),
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'res_model': 'prescription.order.line',
#                 'view_id': self.env.ref('pod_product_custom_options.prescription_order_line_custom_options_form').id,
#                 'res_id': self.id,
#                 'type': 'ir.actions.act_window',
#                 'nodestroy': True,
#                 'target': 'new',
#                 'domain': '[]',
#             }

#     def add_option(self):
#         productObj = self.product_id
#         if productObj.custom_option_ids:
#             wizardObj = self.env['option.selection.wizard'].create({'order_line_id': self.id})
#             return {
#                 'name': ("Information"),
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'src_model': 'prescription.order.line',
#                 'res_model': 'option.selection.wizard',
#                 'view_id': self.env.ref('pod_product_custom_options.option_selection_wizard_form').id,
#                 'res_id': wizardObj.id,
#                 'type': 'ir.actions.act_window',
#                 'nodestroy': True,
#                 'target': 'new',
#             }

#     def update_description_with_options(self, new_custom_option):
#         if not self.description_custom:
#             self.description_custom = ''
#         self.description_custom += f"\n{new_custom_option.custom_option_id.name}: {new_custom_option.input_data}"
#         if new_custom_option.laterality:
#             laterality_display = self.get_laterality_display()
#             self.description_custom += f" - {laterality_display}"


#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the SO line.
#         """
#         for line in self:
#             tax_results = self.env['account.tax']._compute_taxes([
#                 line._convert_to_tax_base_line_dict()
#             ])
#             totals = list(tax_results['totals'].values())[0]
#             amount_untaxed = totals['amount_untaxed']
#             amount_tax = totals['amount_tax']

#             line.update({
#                 'price_subtotal': amount_untaxed,
#                 'price_tax': amount_tax,
#                 'price_total': amount_untaxed + amount_tax,
#             })

#     @api.depends('price_subtotal', 'product_uom_qty')
#     def _compute_price_reduce_taxexcl(self):
#         for line in self:
#             line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

#     @api.depends('price_total', 'product_uom_qty')
#     def _compute_price_reduce_taxinc(self):
#         for line in self:
#             line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0


#     def calculate_total_price(self):
#         base_price = self.price_unit
#         options_price = sum(option.price for option in self.prescription_options_ids)
#         laterality_factor = 2 if any(option.laterality == 'bilateral' for option in self.prescription_options_ids) else 1
#         adjusted_base_price = base_price * laterality_factor
#         total_price = adjusted_base_price + options_price
#         self.price_total = total_price  

#     def save_option(self):
#         product = self.product_id.with_context(
#             lang=self.order_id.partner_id.lang,
#             partner=self.order_id.partner_id.id,
#             quantity=self.product_uom_qty,
#             date=self.order_id.date_order,
#             pricelist=self.order_id.pricelist_id.id,
#             uom=self.product_uom.id
#         )
#         name = product.name_get()[0][1]
#         if product.description_prescription:
#             name += '\n' + product.description_prescription
#         if self.order_id.pricelist_id and self.order_id.partner_id:
#             price_unit = self.env['account.tax']._fix_tax_included_price_company(
#                 self.order_id.pricelist_id._get_product_price(
#                     product, self.product_uom_qty, self.order_id.partner_id),
#                 product.taxes_id, self.tax_id, self.company_id
#             )
#         prescription_options_price = self.prescription_options_price
#         if self.laterality == 'bl_pair':
#             price_unit *= 2 

#         price_unit += prescription_options_price
#         description = self.prescription_options_ids.mapped(lambda option: option.custom_option_id.name+': '+option.input_data if option.custom_option_id and option.input_data else '')
#         if description:
#             name += '\n' + '\n'.join(description)
#         self.name = name
#         self.price_unit = price_unit
#         if self.discount:
#             getperem =self.env['ir.config_parameter'].sudo().get_param('account.show_line_subtotals_tax_selection')
#             if getperem == 'tax_included':
#                 taxes = self.tax_id.compute_all(price_unit, self.order_id.currency_id, self.product_uom_qty, product=self.product_id, partner=self.order_id.partner_shipping_id)
#                 self.non_discount_option_price = taxes['total_included'] / self.product_uom_qty
#             else:
#                 self.non_discount_option_price = price_unit




