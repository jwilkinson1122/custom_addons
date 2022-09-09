# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_patient_rounding_treatment(models.Model):
    _name = 'podiatry.patient.rounding.treatment'
    _description = 'podiatry patient rounding treatment'

    treatment_id = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one('stock.production.lot',
                             string='Lot', required=True)
    short_comment = fields.Char(string='Comment')
    product_id = fields.Many2one('product.product', string='Product')
    podiatry_patient_rounding_treatment_id = fields.Many2one(
        'podiatry.patient.rounding', string="Treatments")
