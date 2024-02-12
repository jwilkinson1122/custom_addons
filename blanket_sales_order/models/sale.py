# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_so_id = fields.Many2one(
        'prescription',
        string="Prescription"
    )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        if self.order_id.prescription_so_id:
            for line in self.order_id.prescription_so_id.order_line.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom != self.product_uom:
                    self.price_unit = line.product_uom._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break    

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if self.order_id.prescription_so_id:
            for line in self.order_id.prescription_so_id.order_line.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom != self.product_uom:
                    self.price_unit = line.product_uom._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break
