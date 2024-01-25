# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pod_owner_id = fields.Many2one("res.partner", string="Billing Physician", compute="compute_pod_medical_billing_id", store=True)
    pod_practice_id = fields.Many2one('res.partner', string='Practice', compute='compute_pod_practice_id', store=True)
    pod_organization_id = fields.Many2one('res.partner', string='Organization', compute='compute_pod_organization_id', store=True)
    pod_sales_partner_id = fields.Many2one("res.partner", string='Pod Partner', compute="compute_pod_sales_partner_id", store=True)
    pod_medical_record_number = fields.Char(compute="compute_pod_medical_record_number", store=True)
    pod_order_uuid = fields.Char(string="Order UUID", index=True, copy=False)

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_medical_billing_id',
                 'partner_id.parent_id.pod_medical_billing_id')
    def compute_pod_medical_billing_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_owner_id': picking.partner_id.parent_id.pod_medical_billing_id.id or
                                            picking.partner_id.pod_medical_billing_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_medical_record_number',
                 'partner_id.parent_id.pod_medical_record_number')
    def compute_pod_medical_record_number(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_medical_record_number': picking.partner_id.parent_id.pod_medical_record_number or
                                                         picking.partner_id.pod_medical_record_number or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_practice_id',
                 'partner_id.parent_id.pod_practice_id')
    def compute_pod_practice_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_practice_id': picking.partner_id.parent_id.pod_practice_id.id or
                                               picking.partner_id.pod_practice_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_organization_id',
                 'partner_id.parent_id.pod_organization_id')
    def compute_pod_organization_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_organization_id': picking.partner_id.parent_id.pod_organization_id.id or
                                                   picking.partner_id.pod_organization_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_sales_partner_id',
                 'partner_id.parent_id.pod_sales_partner_id')
    def compute_pod_sales_partner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_sales_partner_id': picking.partner_id.parent_id.pod_sales_partner_id.id or
                                                   picking.partner_id.pod_sales_partner_id.id or False})
