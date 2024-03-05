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
    
    is_custom_product = fields.Boolean("Have custom options")

    prescription_options_ids = fields.One2many(
        'prescription.custom.options', 'order_line_id',string="Custom Options")
    prescription_options_price = fields.Float(string="Price",
        compute='_compute_options_price',
        digits=dp.get_precision('Product Price'),
        help="Price for the custom option.")
    non_discount_option_price = fields.Float(string="Non Discount Option Price",
        digits=dp.get_precision('Product Price'),
        help="Price for the non discount with custom options product price.")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.custom_option_ids:
            self.is_custom_product = True
        else:
            self.is_custom_product = False


    def _compute_options_price(self):
        for line in self:
            line.prescription_options_price = sum(line.prescription_options_ids.mapped('price'))


    def configure_product(self):
        productObj = self.product_id
        if productObj.custom_option_ids:
            return {
                'name': ("Information"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'prescription.order.line',
                'view_id': self.env.ref('pod_product_custom_options.prescription_order_line_custom_options_form').id,
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
            }


    def add_option(self):
        productObj = self.product_id
        if productObj.custom_option_ids:
            wizardObj = self.env['option.selection.wizard'].create({'order_line_id': self.id})
            return {
                'name': ("Information"),
                'view_mode': 'form',
                'view_type': 'form',
                'src_model': 'prescription.order.line',
                'res_model': 'option.selection.wizard',
                'view_id': self.env.ref('pod_product_custom_options.option_selection_wizard_form').id,
                'res_id': wizardObj.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
            }

    def save_option(self):
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.name_get()[0][1]
        if product.description_prescription:
            name += '\n' + product.description_prescription
        if self.order_id.pricelist_id and self.order_id.partner_id:
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                self.order_id.pricelist_id._get_product_price(
                    product, self.product_uom_qty, self.order_id.partner_id),
                product.taxes_id, self.tax_id, self.company_id
            )
        prescription_options_price = self.prescription_options_price
        if self.laterality == 'bl_pair':
            price_unit *= 2 

        price_unit += prescription_options_price
        description = self.prescription_options_ids.mapped(lambda option: option.custom_option_id.name+': '+option.input_data if option.custom_option_id and option.input_data else '')
        if description:
            name += '\n' + '\n'.join(description)
        self.name = name
        self.price_unit = price_unit
        if self.discount:
            getperem =self.env['ir.config_parameter'].sudo().get_param('account.show_line_subtotals_tax_selection')
            if getperem == 'tax_included':
                taxes = self.tax_id.compute_all(price_unit, self.order_id.currency_id, self.product_uom_qty, product=self.product_id, partner=self.order_id.partner_shipping_id)
                self.non_discount_option_price = taxes['total_included'] / self.product_uom_qty
            else:
                self.non_discount_option_price = price_unit



