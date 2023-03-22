# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_prescription_line(models.Model):
    _name = "medical.prescription.line"
    _description = 'medical prescription line'
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

    name = fields.Many2one('medical.prescription.order','Prescription ID')
    prescription_id = fields.Many2one(
        "medical.prescription.order", "Prescription ID", ondelete="cascade")
    product_id = fields.Many2one('product.product', 'Name')
    prnt = fields.Boolean('Print')
    quantity = fields.Integer('Quantity')
    qty = fields.Integer('x')
    review = fields.Datetime('Review')
    short_comment = fields.Char('Comment', size=128 )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
