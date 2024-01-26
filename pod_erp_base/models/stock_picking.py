# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    owner_id = fields.Many2one("res.partner", string="Billing", compute="compute_pod_billing_id", store=True)
    pod_location_id = fields.Many2one('res.partner', string='Location', compute='compute_pod_location_id', store=True)
    pod_account_id = fields.Many2one('res.partner', string='Practice', compute='compute_pod_account_id', store=True)
    pod_sales_partner_id = fields.Many2one("res.partner", string='Partner', compute="compute_pod_sales_partner_id", store=True)
    record_num = fields.Char(compute="compute_record_num", store=True)
    pod_order_uuid = fields.Char(string="Order UUID", index=True, copy=False)

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_billing_id',
                 'partner_id.parent_id.pod_billing_id')
    def compute_pod_billing_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'owner_id': picking.partner_id.parent_id.pod_billing_id.id or
                                            picking.partner_id.pod_billing_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.record_num',
                 'partner_id.parent_id.record_num')
    def compute_record_num(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'record_num': picking.partner_id.parent_id.record_num or
                                                         picking.partner_id.record_num or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_location_id',
                 'partner_id.parent_id.pod_location_id')
    def compute_pod_location_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_location_id': picking.partner_id.parent_id.pod_location_id.id or
                                               picking.partner_id.pod_location_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_account_id',
                 'partner_id.parent_id.pod_account_id')
    def compute_pod_account_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_account_id': picking.partner_id.parent_id.pod_account_id.id or
                                                   picking.partner_id.pod_account_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.pod_sales_partner_id',
                 'partner_id.parent_id.pod_sales_partner_id')
    def compute_pod_sales_partner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'pod_sales_partner_id': picking.partner_id.parent_id.pod_sales_partner_id.id or
                                                   picking.partner_id.pod_sales_partner_id.id or False})
