# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class podiatry_patient_rounding_medicament(models.Model):
    _name = 'podiatry.patient.rounding.medicament'
    _description = 'podiatry patient rounding medicament'
    
    medicament_id = fields.Many2one('podiatry.medicament',string='Medicament',required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one('stock.production.lot',string='Lot',required=True)
    short_comment = fields.Char(string='Comment')
    product_id = fields.Many2one('product.product',string='Product')
    podiatry_patient_rounding_medicament_id = fields.Many2one('podiatry.patient.rounding',string="Medicaments") 

