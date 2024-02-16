# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Account",
        required=True, change_default=True, index=True,
        tracking=1,
        domain=[('is_company','=',True)], 
        # domain="[('company_id', 'in', (False, company_id))]"
        )
    
    location_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_location','=',True)], 
        string="Location"
        )
    
    practitioner_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_practitioner','=',True)], 
        string="Practitioner"
        )
    

    patient_id = fields.Many2one(
        "prescription.patient", 
        string="Patient",
        required=True, 
        index=True, 
        # states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    )

    prescription_so_id = fields.Many2one('prescription.order', string="Prescription", readonly=False) 

    # prescription_rx_lines = fields.One2many('prescription.order.line', 'order_id', readonly=False)


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
