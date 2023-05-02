# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class orthotic(models.Model):
  
    _name = 'podiatry.orthotic'
    _description = 'Podiatry Orthotic'
    _rec_name = 'product_id'

    @api.depends('product_id')
    def onchange_product(self):
        for each in self:
            if each:
                self.qty_available = self.product_id.qty_available
                self.price = self.product_id.lst_price
            else:
                self.qty_available = 0
                self.price = 0.0

    product_id  = fields.Many2one('product.product', 'Name')
    therapeutic_action = fields.Char('Therapeutic effect', help = 'Therapeutic action')
    price = fields.Float(compute=onchange_product,string='Price',store=True)
    qty_available = fields.Integer(compute=onchange_product,string='Quantity Available',store=True)
    indications = fields.Text('Indications')
    active_component = fields.Char(string="Active Component")
    presentation = fields.Text('Presentation')
    composition = fields.Text('Composition')
    measure = fields.Text('Measure Instructions')
    overmeasure = fields.Text('Overmeasure')
    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Condition')
    notes = fields.Text('Extra Info')

