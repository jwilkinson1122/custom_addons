# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class patient_rounding_supply(models.Model):
    _name = 'podiatry.patient.rounding.supply'
    _description = 'podiatry patient rounding podiatry supply'
    
    product_id = fields.Many2one('product.product',string="Podiatry Supply",required=True)
    short_comment = fields.Char(string='Comment')
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one('stock.production.lot',string='Lot',required=True)
    patient_rounding_supply_id = fields.Many2one('podiatry.patient.rounding',string=" Podiatry Supplies ")

