# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pod_uuid = fields.Char(compute="compute_pod_uuid", store=True)
    pod_order_uuid = fields.Char(string="Order UUID", index=True, copy=False)
    pod_owner_id = fields.Many2one("res.partner", string="Billing Physician", compute="compute_pod_owner_id", store=True)
    pod_practice_id = fields.Many2one('res.partner', string='Practice', compute='compute_pod_practice_id', store=True)
    pod_medical_id = fields.Many2one('res.partner', string='Primary Physician', compute="compute_pod_medical_id", store=True)
    pod_medical_coach_id = fields.Many2one('res.partner', string='Nurse Coach', compute="compute_pod_medical_coach_id", store=True)
    pod_organization_id = fields.Many2one('res.partner', string='Organization', compute='compute_pod_organization_id', store=True)
    pod_medical_billing_id = fields.Many2one('res.partner', string='Billing Physician', compute="compute_pod_medical_billing_id", store=True)
    pod_sales_partner_id = fields.Many2one("res.partner", string="Pod Partner",
                                           compute="compute_pod_sales_partner_id", store=True)
    pod_app_url = fields.Char(string="Pod App URL")
    pod_customer_phone = fields.Char(compute="compute_pod_customer_phone", store=True)

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        # Adding parent ID of medical coach to followers if available
        if res.partner_id and res.pod_medical_coach_id:
            if res.pod_medical_coach_id.parent_id:
                self.env["mail.followers"].create(
                    {
                        "res_model": "sale.order",
                        "res_id": res.id,
                        "partner_id": res.pod_medical_coach_id.parent_id.id,
                    })
        return res

    @api.depends('partner_id', 'partner_id.pod_uuid')
    def compute_pod_uuid(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_uuid': sale.partner_id.pod_uuid or False})

    @api.depends('partner_id', 'partner_id.pod_medical_billing_id')
    def compute_pod_owner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_owner_id': sale.partner_id.pod_medical_billing_id and
                                         sale.partner_id.pod_medical_billing_id.id or False})

    @api.depends('partner_id', 'partner_id.pod_medical_id')
    def compute_pod_medical_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_medical_id': sale.partner_id.pod_medical_id and sale.partner_id.pod_medical_id.id
                                           or False})

    @api.depends('partner_id', 'partner_id.pod_medical_coach_id')
    def compute_pod_medical_coach_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_medical_coach_id': sale.partner_id.pod_medical_coach_id and
                                                 sale.partner_id.pod_medical_coach_id.id or False})

    @api.depends('partner_id', 'partner_id.pod_medical_billing_id')
    def compute_pod_medical_billing_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_medical_billing_id': sale.partner_id.pod_medical_billing_id and
                                                   sale.partner_id.pod_medical_billing_id.id or False})

    @api.depends('partner_id', 'partner_id.pod_sales_partner_id')
    def compute_pod_sales_partner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_sales_partner_id': sale.partner_id.pod_sales_partner_id and
                                                 sale.partner_id.pod_sales_partner_id.id or False})

    @api.depends('partner_id', 'partner_id.phone')
    def compute_pod_customer_phone(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_customer_phone': sale.partner_id.phone or False})

    @api.depends('partner_id', 'partner_id.pod_practice_id')
    def compute_pod_practice_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_practice_id': sale.partner_id.pod_practice_id and sale.partner_id.pod_practice_id.id
                                            or False})

    @api.depends('partner_id', 'partner_id.pod_organization_id')
    def compute_pod_organization_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for sale in self:
            sale.update({'pod_organization_id': sale.partner_id.pod_organization_id and
                                                sale.partner_id.pod_organization_id.id or False})
