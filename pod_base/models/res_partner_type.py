import numbers
import json
from lxml import etree

from odoo import _, api, exceptions, fields, models
from odoo.osv.expression import FALSE_LEAF, OR, is_leaf
from odoo.tools.safe_eval import safe_eval

class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Contact Type'
    _company_inherit_fields = ['company_type', 'customer', 'supplier']
    _person_inherit_fields = ['company_type', 'type']

    id = fields.Integer(readonly=True)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer('Priority', default=10)
    active = fields.Boolean(default=True)
    can_have_parent = fields.Boolean(default=True)
    parent_is_required = fields.Boolean(default=False)
    parent_type_ids = fields.Many2many(
        'res.partner.type', string='Company types authorized for parent',
        relation="res_partner_type_parent_types_rel",
        column1="child_type_id", column2="parent_type_id")
    parent_relation_label = fields.Char(
        'Parent relation label', translate=True, required=True,
        default='attached to')
    subcompanies_label = fields.Char(
        'Sub-companies label', translate=True, required=True,
        default='Sub-companies')
    # Inherited fields for partners of this type
    company_type = fields.Selection([
        ('person', 'Individual'),
        ('company', 'Company'),
    ], 'Company Type', required=True, default='company')
    
    customer = fields.Boolean(string='Is a Customer', default=True)
    supplier = fields.Boolean(string='Is a Vendor')
    
    type = fields.Selection(
        [
            ('contact', 'Contact'),
            ('invoice', 'Invoice address'),
            ('delivery', 'Shipping address'),
            ('other', 'Other address'),
        ], 'Address Type', default='contact',
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
