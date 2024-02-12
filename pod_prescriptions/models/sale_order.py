# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import logging
import base64
import time
import json
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.modules.module import get_module_resource
from odoo import _, api, fields, models, exceptions
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one( 
        comodel_name='res.partner', 
        string="Account", 
        # required=True, 
        change_default=True, 
        index=True, 
        tracking=1, 
        domain=[('is_company','=',True)]
        )
    
    location_id = fields.Many2one(
        'res.partner', 
        # required=True, 
        index=True, 
        domain=[('is_location','=',True)], 
        string="Location"
        )
    
    practitioner_id = fields.Many2one(
        'res.partner', 
        # required=True, 
        index=True, 
        domain=[('is_practitioner','=',True)], 
        string="Practitioner"
        )
    
    patient_id = fields.Many2one(
        "prescriptions.patient", 
        string="Patient", 
        required=True, 
        index=True 
    )

    prescription_order_id = fields.Many2one(
        'prescriptions.order',
        string="Prescription"
    )

    prescription_order_lines = fields.One2many('prescriptions.order.line', 'prescription_order_id', readonly=False)
    order_details_ids = fields.One2many('prescriptions.order.history.line', 'order_id')
    

    @api.onchange('partner_id')
    def sale_order_domain(self):
        self.write({'order_details_ids': [(5,)]})
        new_lines = []
        lines = self.env['sale.order.line'].search(
            [('order_id.partner_id', '=', self.partner_id.id), ('order_id.state', 'in', ('sale', 'done'))])
        for rec in lines:
            new_lines.append((0, 0, {
                'name': rec.order_id.name,
                'product_id': rec.product_id,
                'product_uom_qty': rec.product_uom_qty,
                'price_unit': rec.price_unit,
                'tax_id': rec.tax_id,
                'price_subtotal': rec.price_subtotal
            }))
        self.write({'order_details_ids': new_lines})

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrder, self).product_id_change()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description:
                self.name = product.variant_description
        return res
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.onchange("product_id")
    # def product_id_change(self):
    #     res = super(SaleOrderLine, self).product_id_change()
    #     if self.product_id:
    #         product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
    #         if product.variant_description:
    #             self.name = product.variant_description
    #     return res

    @api.onchange('product_id')
    def product_id_change(self):
        if self.order_id.prescription_order_id:
            for line in self.order_id.prescription_order_id.order_line.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom != self.product_uom:
                    self.price_unit = line.product_uom._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break    

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if self.order_id.prescription_order_id:
            for line in self.order_id.prescription_order_id.order_line.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom != self.product_uom:
                    self.price_unit = line.product_uom._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break

class SaleOrderHistoryLine(models.Model):
    _name = 'sale.order.history.line'
    _description = 'Sale Order History Line'

    order_id = fields.Many2one('sale.order')
    name = fields.Char('Order')
    product_id = fields.Many2one('product.product')
    product_uom_qty = fields.Integer('Quantity')
    price_unit = fields.Integer('Unit price')
    tax_id = fields.Many2many('account.tax')
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    price_subtotal = fields.Integer(string='Subtotal')

    def action_add(self):
        vals = {
            'order_id': self.order_id.id,
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'price_unit': self.price_unit,
            'tax_id': self.tax_id.id,
            'price_subtotal': self.price_subtotal,
            'company_id':self.company_id,
        }
        self.env['sale.order.line'].sudo().create(vals)
