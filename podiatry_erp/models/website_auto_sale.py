# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError


class WebsiteAutoSale(models.Model):
    _name = "website.auto.sale"
    _description = "Website Auto Sale"

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company', string='Company')

    validation_order = fields.Boolean("Validation Order")

    validation_picking = fields.Boolean("Validation Picking")

    create_incoice = fields.Boolean("Create Invoice")
    validate_invoice = fields.Boolean("Vaidate Invoice")

    @api.onchange('validate_invoice')
    def depends_force(self):
        if self.validate_invoice == True:
            self.create_incoice = True

    @api.onchange('validation_picking')
    def depends_transfer(self):
        if self.validation_picking == True:
            self.validation_order = True

    @api.onchange('create_incoice')
    def depends_invoice(self):
        if self.create_incoice == True:
            self.validation_order = True
            self.validation_picking = True
