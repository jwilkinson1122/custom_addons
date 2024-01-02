# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prescriptions_order_id = fields.Many2one(
        'prescriptions.order',
        string="Prescriptions Order"
    )
    # prescriptions_order_lines = fields.One2many(
    #     'prescriptions.order.line', 'order_id', readonly=False)
    
    partner_id = fields.Many2one(
        'res.partner',
        domain=[('is_company','=',True)],
        string="Practice"
        )
    practitioner_id = fields.Many2one(
        'res.partner',
        domain=[('is_practitioner','=',True)],
        string="Practitioner"
        )
    patient_id = fields.Many2one(
        "pod.patient", 
        states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    ) 
    

    @api.onchange('partner_id', 'practitioner_id')
    def onchange_set_domain_partner_practitioner(self):
        if self.partner_id and not self.practitioner_id:
            self.practitioner_id = self.partner_id.practitioner_id
        if self.practitioner_id and not self.patient_id:
            self.patient_id = self.practitioner_id.patient_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        if self.order_id.prescriptions_order_id:
            for line in self.order_id.prescriptions_order_id.line_ids.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom != self.product_uom:
                    self.price_unit = line.product_uom._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break    

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if self.order_id.prescriptions_order_id:
            for line in self.order_id.prescriptions_order_id.line_ids.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom != self.product_uom:
                    self.price_unit = line.product_uom._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break
