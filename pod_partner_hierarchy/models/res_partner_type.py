# -*- coding: utf-8 -*-


from odoo import fields, models

class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Contact Type'
    _company_inherit_fields = ['company_type', 'type', 'is_account', 'is_affiliate']
    _person_inherit_fields = ['company_type', 'type', 'is_contact', 'is_patient']

    id = fields.Integer(readonly=True)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)  
    sequence = fields.Integer('Priority', default=10)
    active = fields.Boolean(default=True)

    
    is_account = fields.Boolean(string='Account', help="Check this box if this is a customer account.")
    is_affiliate = fields.Boolean(string='Affiliate', help="Check this box if this is an affiliate.")
    is_contact = fields.Boolean(string='Contact', help="Check this box if this is a contact.")
    is_patient = fields.Boolean(string='Patient', help="Check this box if this is a patient.")

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
    ], 'Company Type', required=True, default='company')
    
    type = fields.Selection(
        [
            ('contact', 'Contact Address'),
            ('patient', 'Patient Address'),
            ('invoice', 'Invoice address'),
            ('delivery', 'Shipping address'),
            ('other', 'Other address'),
        ], 'Address Type', default=False,
        help="Used to select automatically the right address "
        "according to the context in sales and purchases documents.")
    
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