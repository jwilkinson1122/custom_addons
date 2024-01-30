# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    internal_identifier = fields.Char(compute="compute_internal_identifier", store=True)
    order_internal_code = fields.Char(string="Order UUID", index=True, copy=False)
    owner_id = fields.Many2one("res.partner", string="Billing", compute="compute_owner_id", store=True)
    parent_id = fields.Many2one('res.partner', string='Practice', compute='compute_parent_id', store=True)
    location_ids = fields.Many2one('res.partner', string='Location', compute='compute_location_ids', store=True)
    child_ids = fields.Many2one('res.partner', string='Practitioner', compute="compute_child_ids", store=True)
    assistant_id = fields.Many2one('res.partner', string='Medical Assitant', compute="compute_assistant_id", store=True)
    billing_id = fields.Many2one('res.partner', string='Billing', compute="compute_billing_id", store=True)
    sales_partner_id = fields.Many2one("res.partner", string="Partner",
                                           compute="compute_sales_partner_id", store=True)
    app_url = fields.Char(string="App URL")
    customer_phone = fields.Char(compute="compute_customer_phone", store=True)

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        # Adding parent ID of medical assistant to followers if available
        if res.partner_id and res.assistant_id:
            if res.assistant_id.parent_id:
                self.env["mail.followers"].create(
                    {
                        "res_model": "sale.order",
                        "res_id": res.id,
                        "partner_id": res.assistant_id.parent_id.id,
                    })
        return res

    @api.depends('partner_id', 'partner_id.internal_identifier')
    def compute_internal_identifier(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'internal_identifier': sale.partner_id.internal_identifier or False})

    @api.depends('partner_id', 'partner_id.billing_id')
    def compute_owner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'owner_id': sale.partner_id.billing_id and
                                         sale.partner_id.billing_id.id or False})

    @api.depends('partner_id', 'partner_id.child_ids')
    def compute_child_ids(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'child_ids': sale.partner_id.child_ids and sale.partner_id.child_ids.id
                                           or False})

    @api.depends('partner_id', 'partner_id.assistant_id')
    def compute_assistant_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'assistant_id': sale.partner_id.assistant_id and
                                                 sale.partner_id.assistant_id.id or False})

    @api.depends('partner_id', 'partner_id.billing_id')
    def compute_billing_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'billing_id': sale.partner_id.billing_id and
                                                   sale.partner_id.billing_id.id or False})

    @api.depends('partner_id', 'partner_id.sales_partner_id')
    def compute_sales_partner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'sales_partner_id': sale.partner_id.sales_partner_id and
                                                 sale.partner_id.sales_partner_id.id or False})

    @api.depends('partner_id', 'partner_id.phone')
    def compute_customer_phone(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'customer_phone': sale.partner_id.phone or False})

    @api.depends('partner_id', 'partner_id.location_ids')
    def compute_location_ids(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'location_ids': sale.partner_id.location_ids and sale.partner_id.location_ids.id
                                            or False})

    @api.depends('partner_id', 'partner_id.parent_id')
    def compute_parent_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'parent_id': sale.partner_id.parent_id and
                                                sale.partner_id.parent_id.id or False})
