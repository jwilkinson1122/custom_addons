# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Partner Type'
    _company_inherit_fields = ['company_type', 'type', 'is_company', 'is_account', 'is_affiliate']
    _person_inherit_fields = ['company_type', 'type', 'is_contact', 'is_patient']


    @api.constrains('company_type', 'is_contact', 'is_patient', 'is_affiliate', 'is_account')
    def _check_company_type_consistency(self):
        for rec in self:
            if rec.company_type == 'company' and (rec.is_contact or rec.is_patient):
                raise ValidationError("Company types cannot be marked as contacts or patients.")
            if rec.company_type == 'person' and (rec.is_account or rec.is_affiliate):
                raise ValidationError("Person types cannot be marked as accounts or affiliates.")

    @api.constrains('company_type', 'is_contact')
    def _check_contact_company_type_consistency(self):
        for rec in self:
            if rec.is_contact and rec.company_type == 'company':
                raise ValidationError("Contact types must have company_type = 'person'.")


    id = fields.Integer(readonly=True)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)  
    sequence = fields.Integer('Priority', default=10)
    active = fields.Boolean(default=True)

    is_company = fields.Boolean(string='Company', help="Check this box if this is a company.")
    is_account = fields.Boolean(string='Account', help="Check this box if this is a customer account.")
    is_affiliate = fields.Boolean(string='Affiliate', help="Check this box if this is an affiliate.")
    is_contact = fields.Boolean(string='Contact', help="Check this box if this is a contact.")
    is_patient = fields.Boolean(string='Patient', help="Check this box if this is a patient.")

    channel_partner_ids = fields.Many2many(
        'res.partner',
        'res_partner_type_channel_rel',
        'type_id',
        'partner_id',
        string="Channel Partners"
    )

    # Partners hierarchy
    can_have_parent = fields.Boolean(default=True)
    parent_is_required = fields.Boolean(default=False)
    parent_type_ids = fields.Many2many(
        'res.partner.type', string='Company types authorized for parent',
        relation="res_partner_type_parent_types_rel",
        column1="child_type_id", column2="parent_type_id")

    parent_relation_label = fields.Char(
        'Parent relation label', translate=True, required=True,
        default='Attached To:')
    companies_label = fields.Char(
        'Companies label', translate=True, required=True,
        default='Companies')
    contacts_label = fields.Char(
        'Contacts label', translate=True, required=True,
        default='Contacts')

    # Inherited fields for partners of this type
    company_type = fields.Selection([
        ('person', 'Individual'),
        ('company', 'Company'),
    ], 'Company Type', required=True, default='person')
    
    # company_type is only an interface field, do not use it in business logic
    # company_type = fields.Selection(string='Company Type',
    #     selection=[('person', 'Individual'), ('company', 'Company')],
    #     compute='_compute_company_type', inverse='_write_company_type')
    
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
        ], string='Address Type',
        default='contact',
        help="- Contact: Add details of contacts of this company.\n"
             "- Invoice Address: Preferred address for all invoices. Selected by default when you invoice an order that belongs to this company.\n"
             "- Delivery Address: Preferred address for all deliveries. Selected by default when you deliver an order that belongs to this company.\n"
             "- Other: Other address for the company (e.g. subsidiary, ...)")
    
    # Inherited fields for the children with a parent of this type
    field_ids = fields.Many2many(
        'ir.model.fields', domain=[
            ('model', '=', 'res.partner'),
            ('store', '=', True),
            ('ttype', '!=', 'one2many'),
        ], string="Fields to update in children")

    partner_display_name = fields.Char(
        default='partner.name_get()[0][1]',
        help="The variable 'partner' represents the partner "
        "for which we compute the display name")
    
    
    # @api.depends('is_company')
    # def _compute_company_type(self):
    #     for partner in self:
    #         partner.company_type = 'company' if partner.is_company else 'person'

    # def _write_company_type(self):
    #     for partner in self:
    #         partner.is_company = partner.company_type == 'company'

    # @api.onchange('company_type')
    # def onchange_company_type(self):
    #     self.is_company = (self.company_type == 'company')