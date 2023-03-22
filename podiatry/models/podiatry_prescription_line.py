# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class PrescriptionLine(models.Model):
    _name = "podiatry.prescription.line"
    _description = 'podiatry prescription line'
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

    name = fields.Many2one('podiatry.prescription','Prescription ID')
    product_id  = fields.Many2one('product.product', 'Name')
    price = fields.Float(compute=onchange_product,string='Price',store=True)
    qty_available = fields.Integer(compute=onchange_product,string='Quantity Available',store=True)
    qty = fields.Integer('x')
    quantity = fields.Integer('Quantity')
    prnt = fields.Boolean('Print')
    notes = fields.Text('Extra Info')

  


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
