# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class patient_rounding_orthotic(models.Model):
    _name = 'podiatry.patient.rounding.orthotic'
    _description = 'podiatry patient rounding orthotic'
    
    orthotic_id = fields.Many2one('podiatry.orthotic',string='Orthotic',required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one('stock.production.lot',string='Lot',required=True)
    short_comment = fields.Char(string='Comment')
    product_id = fields.Many2one('product.product',string='Product')
    patient_rounding_orthotic_id = fields.Many2one('podiatry.patient.rounding',string="Orthotics") 

