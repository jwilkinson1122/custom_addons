# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contact_internal_code = fields.Char(compute="compute_contact_internal_code", store=True)
    order_internal_code = fields.Char(string="Order UUID", index=True, copy=False)
    owner_id = fields.Many2one("res.partner", string="Billing", compute="compute_owner_id", store=True)
    pod_account_id = fields.Many2one('res.partner', string='Practice', compute='compute_pod_account_id', store=True)
    pod_location_id = fields.Many2one('res.partner', string='Location', compute='compute_pod_location_id', store=True)
    pod_practitioner_id = fields.Many2one('res.partner', string='Practitioner', compute="compute_pod_practitioner_id", store=True)
    pod_assistant_id = fields.Many2one('res.partner', string='Medical Assitant', compute="compute_pod_assistant_id", store=True)
    pod_billing_id = fields.Many2one('res.partner', string='Billing', compute="compute_pod_billing_id", store=True)
    pod_sales_partner_id = fields.Many2one("res.partner", string="Partner",
                                           compute="compute_pod_sales_partner_id", store=True)
    app_url = fields.Char(string="App URL")
    customer_phone = fields.Char(compute="compute_customer_phone", store=True)

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        # Adding parent ID of medical assistant to followers if available
        if res.partner_id and res.pod_assistant_id:
            if res.pod_assistant_id.parent_id:
                self.env["mail.followers"].create(
                    {
                        "res_model": "sale.order",
                        "res_id": res.id,
                        "partner_id": res.pod_assistant_id.parent_id.id,
                    })
        return res

    @api.depends('partner_id', 'partner_id.contact_internal_code')
    def compute_contact_internal_code(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'contact_internal_code': sale.partner_id.contact_internal_code or False})

    @api.depends('partner_id', 'partner_id.pod_billing_id')
    def compute_owner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'owner_id': sale.partner_id.pod_billing_id and
                                         sale.partner_id.pod_billing_id.id or False})

    @api.depends('partner_id', 'partner_id.pod_practitioner_id')
    def compute_pod_practitioner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_practitioner_id': sale.partner_id.pod_practitioner_id and sale.partner_id.pod_practitioner_id.id
                                           or False})

    @api.depends('partner_id', 'partner_id.pod_assistant_id')
    def compute_pod_assistant_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_assistant_id': sale.partner_id.pod_assistant_id and
                                                 sale.partner_id.pod_assistant_id.id or False})

    @api.depends('partner_id', 'partner_id.pod_billing_id')
    def compute_pod_billing_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_billing_id': sale.partner_id.pod_billing_id and
                                                   sale.partner_id.pod_billing_id.id or False})

    @api.depends('partner_id', 'partner_id.pod_sales_partner_id')
    def compute_pod_sales_partner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_sales_partner_id': sale.partner_id.pod_sales_partner_id and
                                                 sale.partner_id.pod_sales_partner_id.id or False})

    @api.depends('partner_id', 'partner_id.phone')
    def compute_customer_phone(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'customer_phone': sale.partner_id.phone or False})

    @api.depends('partner_id', 'partner_id.pod_location_id')
    def compute_pod_location_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_location_id': sale.partner_id.pod_location_id and sale.partner_id.pod_location_id.id
                                            or False})

    @api.depends('partner_id', 'partner_id.pod_account_id')
    def compute_pod_account_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_account_id': sale.partner_id.pod_account_id and
                                                sale.partner_id.pod_account_id.id or False})
