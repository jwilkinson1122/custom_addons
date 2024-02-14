# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MaterialOfRepair(models.Model):
    """Material Of Repair"""
    _name = 'material.of.repair'
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', domain=[('is_orthotic_part', '=', True)], string="Part Name",
                                 required=True)
    serial_number = fields.Char(related="product_id.barcode", string="Serial Number", translate=True)
    product_qty = fields.Float(string="Quantity", required=True, default=1)
    uom_id = fields.Many2one('uom.uom', string="Unit", required=True)
    remarks = fields.Char(string="Remarks", translate=True)
    price = fields.Monetary(string="Price")
    sub_total = fields.Monetary(string="Sub Total", compute='_get_part_sub_total')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order', string="MRO")

    @api.onchange('product_id')
    def material_of_repair_details(self):
        for rec in self:
            if rec.product_id:
                rec.price = rec.product_id.lst_price
                rec.uom_id = rec.product_id.uom_id

    @api.depends('product_qty', 'price')
    def _get_part_sub_total(self):
        for rec in self:
            rec.sub_total = rec.product_qty * rec.price


class MroQuotation(models.Model):
    """MRO Quotation"""
    _name = 'mro.quotation'
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Part Name", domain="[('is_orthotic_part','=',True)]",
                                 required=True)
    serial_number = fields.Char(related="product_id.barcode", string="Serial Number", translate=True)
    qty = fields.Float(string="Quantity", required=True, default=1)
    uom_id = fields.Many2one('uom.uom', string="Unit")
    remarks = fields.Char(string="Remarks", translate=True)
    project_task_id = fields.Many2one('project.task')

    @api.onchange('product_id')
    def _part_price(self):
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id
