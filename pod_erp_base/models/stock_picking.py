# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    owner_id = fields.Many2one("res.partner", string="Billing", compute="compute_billing_id", store=True)
    location_ids = fields.Many2one('res.partner', string='Location', compute='compute_location_ids', store=True)
    parent_id = fields.Many2one('res.partner', string='Practice', compute='compute_parent_id', store=True)
    sales_partner_id = fields.Many2one("res.partner", string='Partner', compute="compute_sales_partner_id", store=True)
    record_num = fields.Char(compute="compute_record_num", store=True)
    order_internal_code = fields.Char(string="Order UUID", index=True, copy=False)

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.billing_id',
                 'partner_id.parent_id.billing_id')
    def compute_billing_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'owner_id': picking.partner_id.parent_id.billing_id.id or
                                            picking.partner_id.billing_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.record_num',
                 'partner_id.parent_id.record_num')
    def compute_record_num(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'record_num': picking.partner_id.parent_id.record_num or
                                                         picking.partner_id.record_num or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.location_ids',
                 'partner_id.parent_id.location_ids')
    def compute_location_ids(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'location_ids': picking.partner_id.parent_id.location_ids.id or
                                               picking.partner_id.location_ids.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.parent_id',
                 'partner_id.parent_id.parent_id')
    def compute_parent_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'parent_id': picking.partner_id.parent_id.parent_id.id or
                                                   picking.partner_id.parent_id.id or False})

    @api.depends('partner_id', 'partner_id.parent_id', 'partner_id.sales_partner_id',
                 'partner_id.parent_id.sales_partner_id')
    def compute_sales_partner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for picking in self:
            picking.update({'sales_partner_id': picking.partner_id.parent_id.sales_partner_id.id or
                                                   picking.partner_id.sales_partner_id.id or False})
