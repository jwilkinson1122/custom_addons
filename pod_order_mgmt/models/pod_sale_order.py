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



class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'
    
    practice_id = fields.Many2one(
        'res.partner',
        # required=True,
        domain=[('is_company','=',True)],
        string="Practice"
        )
    practitioner_id = fields.Many2one(
        'res.partner',
        # required=True,
        domain=[('is_practitioner','=',True)],
        string="Practitioner"
        )
    patient_id = fields.Many2one(
        "pod.patient", 
        # required=True,
        states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    ) 
    
    prescription_order_id = fields.Many2one('pod.prescription.order', readonly=False) 
    prescription_order_lines = fields.One2many('pod.prescription.order.line', 'prescription_order_id', readonly=False)
    order_details_ids = fields.One2many('order.history.line', 'order_id')
    
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
        res = super(InheritedSaleOrder, self).product_id_change()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description:
                self.name = product.variant_description
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description:
                self.name = product.variant_description
        return res
    
class OrderHistoryLine(models.Model):
    _name = 'order.history.line'
    _description = 'Order History Line'

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
