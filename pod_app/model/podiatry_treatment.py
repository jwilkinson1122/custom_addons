# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_treatment(models.Model):

    _name = 'podiatry.treatment'
    _description = 'Podiatry Treatment'
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

    product_id = fields.Many2one('product.product', 'Name')
    corrective_action = fields.Char(
        'Corrective effect', help='Corrective action')
    price = fields.Float(compute=onchange_product, string='Price', store=True)
    qty_available = fields.Integer(
        compute=onchange_product, string='Quantity Available', store=True)
    components = fields.Char(string="Components")
    presentation = fields.Text('Presentation')
    composition = fields.Text('Composition')
    quantity = fields.Text('Quatity Instructions')
    notes = fields.Text('Extra Info')
