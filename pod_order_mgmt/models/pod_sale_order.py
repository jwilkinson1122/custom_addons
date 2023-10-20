# -*- coding: utf-8 -*-
import logging
import base64
import time
import json
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.modules.module import get_module_resource
from odoo import _, api, fields, models, exceptions
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang



class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'
    
    practice_id = fields.Many2one(
        'res.partner',
        # required=True,
        domain=[('is_company','=',True)],
        string="Practice"
        )
    practitioner_id = fields.Many2one(
        'res.partner',
        # required=True,
        domain=[('is_practitioner','=',True)],
        string="Practitioner"
        )
    patient_id = fields.Many2one(
        "pod.patient", 
        # required=True,
        states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    ) 
    
    # patient_id = fields.Char(related='prescription_order_id.patient_id.name')

    prescription_order_id = fields.Many2one('pod.prescription.order', readonly=False) 
    prescription_order_lines = fields.One2many('pod.prescription.order.line', 'prescription_order_id', readonly=False)
    
    @api.onchange('partner_id', 'practitioner_id')
    def onchange_set_domain_partner_practitioner(self):
        if self.partner_id and not self.practitioner_id:
            self.practitioner_id = self.partner_id.practitioner_id
        if self.practitioner_id and not self.patient_id:
            # Set patient_id based on practitioner_id
            self.patient_id = self.practitioner_id.patient_id
    # @api.onchange('partner_id', 'practitioner_id')
    # def _onchange_partner_practitioner(self):
    #     if self.partner_id:
    #         self.practitioner_id = False
    #         self.patient_id = False
            
    #     if self.practitioner_id:
    #         self.patient_id = False
    
    @api.onchange("product_id")
    def product_id_change(self):
        res = super(InheritedSaleOrder, self).product_id_change()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description:
                self.name = product.variant_description
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description:
                self.name = product.variant_description
        return res