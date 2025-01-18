# -*- coding: utf-8 -*-

import logging
import json
from lxml import etree

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    parent_id = fields.Many2one(ondelete='restrict')
    # parent_id = fields.Many2one(
    #     'res.partner', string='Parent Company',
    #     domain="[('is_company', '=', True), '|', ('partner_type_id', '=', False), ('partner_type_id', 'in', parent_type_ids)]",
    #     ondelete='restrict',
    #     help="Select a parent company for this partner."
    # )

    type = fields.Selection(default=False)
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
    parent_type_ids = fields.Many2many(
        'res.partner.type', 
        string='Company types authorized for parent', 
        compute='_compute_parent_types'
    )
    
    affiliate_ids = fields.One2many(
        'res.partner', 
        'parent_id', 
        string='Affiliates',
        compute='_compute_affiliate_ids',
        store=False,  # Avoid saving to the database
        domain=[('is_company', '=', True)]
    )
    
    affiliates_count = fields.Integer('Number of Affiliates', compute='_compute_affiliates_count')
    affiliates_label = fields.Char(related='partner_type_id.affiliates_label', readonly=True)
    
    sub_affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Affiliates",
        compute="_compute_sub_affiliate_ids",
        store=False,
    )

    def _get_all_sub_affiliates(self):
        """
        Recursively fetch all sub-affiliates for the current partner, excluding direct affiliates.
        """
        sub_affiliates = self.env["res.partner"]
        for affiliate in self.affiliate_ids:
            sub_affiliates |= affiliate.affiliate_ids  # Direct affiliates of the current affiliate
            sub_affiliates |= affiliate._get_all_sub_affiliates()  # Recursively fetch deeper levels
        return sub_affiliates

    @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
    def _compute_sub_affiliate_ids(self):
        """
        Compute sub-affiliates for each partner.
        """
        for partner in self:
            all_sub_affiliates = partner._get_all_sub_affiliates()
            partner.sub_affiliate_ids = all_sub_affiliates - partner.affiliate_ids  # Exclude direct affiliates


    contact_ids = fields.One2many('res.partner', 'parent_id', 'Contacts', domain=[('is_company', '=', False)])

    contacts_count = fields.Integer('Number of Contacts', compute='_compute_contacts_count')
    contacts_label = fields.Char(related='partner_type_id.contacts_label', readonly=True)
    
    sub_contact_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Contacts",
        compute="_compute_sub_contact_ids",
        store=False,
    )

    def _get_all_sub_contacts(self):
        """
        Recursively fetch all sub-contacts for the current company,
        excluding direct child contacts.
        """
        sub_contacts = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if not child.is_company:  # Ensure only non-company contacts are processed
                    _logger.debug("Adding direct child contact: %s (ID: %s)", child.name, child.id)
                    sub_contacts |= child  # Include the direct child contact
                # Recursively fetch all contacts for the child, including deeper levels
                sub_contacts |= child._get_all_sub_contacts()
        return sub_contacts

    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_contact_ids(self):
        """
        Compute sub-contacts for the current company.
        """
        for partner in self:
            if partner.is_company:  # Ensure we compute for companies only
                _logger.debug("Computing sub-contacts for company: %s (ID: %s)", partner.name, partner.id)
                all_sub_contacts = partner._get_all_sub_contacts()
                # Exclude direct child contacts from the results
                final_sub_contacts = all_sub_contacts - partner.child_ids.filtered(lambda c: not c.is_company)
                _logger.debug("Final sub-contacts for company %s (ID: %s): %s", partner.name, partner.id, final_sub_contacts)
                partner.sub_contact_ids = final_sub_contacts
            else:
                partner.sub_contact_ids = self.env["res.partner"]  # Empty for non-companies


    # def _get_all_sub_contacts(self):
    #     """
    #     Recursively fetch all sub-contacts for the current partner, excluding direct contacts.
    #     """
    #     sub_contacts = self.env["res.partner"]
    #     for contact in self.contact_ids:  
    #         _logger.debug("Processing contact: %s (ID: %s)", contact.name, contact.id)
    #         sub_contacts |= contact.contact_ids   
    #         _logger.debug("Direct sub-contacts for %s: %s", contact.name, contact.contact_ids)
    #         sub_contacts |= contact._get_all_sub_contacts()  
    #         _logger.debug("Recursive sub-contacts for %s: %s", contact.name, sub_contacts)
    #     _logger.debug("All sub-contacts for partner %s (ID: %s): %s", self.name, self.id, sub_contacts)
    #     return sub_contacts

    # @api.depends("contact_ids", "contact_ids.contact_ids")
    # def _compute_sub_contact_ids(self):
    #     """
    #     Compute sub-contacts for each partner.
    #     """
    #     for partner in self:
    #         _logger.debug("Computing sub-contacts for partner: %s (ID: %s)", partner.name, partner.id)
    #         all_sub_contacts = partner._get_all_sub_contacts()
    #         _logger.debug("All sub-contacts before exclusion for %s: %s", partner.name, all_sub_contacts)
    #         partner.sub_contact_ids = all_sub_contacts - partner.contact_ids   
    #         _logger.debug("Final sub-contacts for partner %s: %s", partner.name, partner.sub_contact_ids)

    parent_relation_label = fields.Char(related='partner_type_id.parent_relation_label', readonly=True)
    customer = fields.Boolean(string='Is a Customer', default=True,
                              help="Check this box if this contact is a customer. It can be selected in sales orders.")
    supplier = fields.Boolean(string='Is a Vendor',
                              help="Check this box if this contact is a vendor. It can be selected in purchase orders.")

    @api.depends('partner_type_id')
    def _compute_parent_types(self):
        for partner in self:
            if partner.partner_type_id:
                partner.parent_type_ids = partner.partner_type_id.parent_type_ids
            else:
                partner.parent_type_ids = self.env['res.partner.type'].browse()

    @api.depends('child_ids')
    def _compute_affiliate_ids(self):
        for partner in self:
            partner.affiliate_ids = partner.child_ids.filtered(lambda c: c.is_company)

    @api.depends('child_ids')
    def _compute_affiliates_count(self):
        affiliates = self.mapped('child_ids').filtered(
            lambda child: child.is_company)
        self.affiliates_count = len(affiliates)

    @api.depends('partner_type_id')
    def _compute_partner_type_infos(self):
        """Compute parent-related fields based on partner type."""
        for partner in self:
            partner.can_have_parent = True
            partner.parent_is_required = False
            if partner.partner_type_id and partner.partner_type_id.can_have_parent:
                partner.can_have_parent = True
                partner.parent_is_required = partner.partner_type_id.parent_is_required

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res['company_type'] = 'company'
        res['partner_type_id'] = self.env['res.partner.type'].search([('code', '=', 'CUSTOMER')], limit=1).id
        return res
    
    @api.onchange('company_type')
    def _onchange_company_type(self):
        code = 'CONTACT'
        if self.company_type == 'company':
            code = 'SUPPLIER' if self.supplier else 'CLIENT'
        self.partner_type_id = self.partner_type_id.search(
            [('code', '=', code)], limit=1)

    @api.onchange('partner_type_id')
    def _onchange_partner_type(self):
        """Handle changes in partner type to update parent-related fields."""
        self.update(self._get_inherit_values(self.partner_type_id))
        if self.partner_type_id and self.partner_type_id.can_have_parent:
            self.can_have_parent = True
        else:
            self.can_have_parent = False

    def _get_inherit_values(self, partner_type, not_null=False):
        if not partner_type:
            return {}
        inherit_fields = getattr(
            partner_type, '_%s_inherit_fields' % partner_type.company_type)
        inherit_values = partner_type.read(inherit_fields)[0]
        if 'id' in inherit_values:
            del inherit_values['id']
        if not_null:
            for fname in list(inherit_values.keys()):
                if not inherit_values[fname]:
                    del inherit_values[fname]
        return inherit_values

    def _update_children(self, vals):
        for partner in self:
            if partner.child_ids and partner.partner_type_id.field_ids:
                children_vals = {
                    key: value for key, value in vals.items()
                    if key in partner.partner_type_id.field_ids.mapped('name')}
                if children_vals:
                    partner.child_ids.write(children_vals)


    @api.model
    def create(self, vals):
        # Safely retrieve the partner_type_id from vals
        partner_type_id = vals.get('partner_type_id')
        partner_type = self.env['res.partner.type'].browse(partner_type_id) if partner_type_id else self.env['res.partner.type']
        
        if partner_type:
            # _logger.debug(f"Partner Type: {partner_type.display_name if partner_type.display_name else 'No Display Name'}")
            vals.update(self._get_inherit_values(partner_type))
        
        new_partner = super(ResPartner, self).create(vals)
        new_partner._update_children(vals)
        return new_partner


    def write(self, vals):
        partners_by_type = {}
        if vals.get('partner_type_id'):
            partner_type = self.env['res.partner.type'].browse(
                vals['partner_type_id'])
            partners_by_type[partner_type] = self
        else:
            for partner in self:
                partners_by_type.setdefault(
                    partner.partner_type_id, self.browse())
                partners_by_type[partner.partner_type_id] |= partner
        for partner_type in partners_by_type:
            if list(vals.keys()) != ['is_company']:  # To avoid infinite loop
                vals.update(self._get_inherit_values(
                    partner_type, not_null=True))
            super(ResPartner, partners_by_type[partner_type]).write(vals)
        self._update_children(vals)
        return True

    def view_affiliates(self):
        return {
            'name': _('Affiliates'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'tree,form',
            'view_id': False,
            'domain': [
                ('parent_id', 'in', self.ids),
                ('is_company', '=', True)
            ],
            'target': 'current',
        }

    def _update_fields_view_get_result(self, result, view_type='form'):
        if view_type == 'form' and not self._context.get(
            'display_original_view'):
            # In order to inherit all views based on the field order_line
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field[@name='child_ids']"):
                node.set('name', 'contact_ids')
                node.set('modifiers', json.dumps(
                    {'default_customer': False, 'default_supplier': False}))
                result['fields']['contact_ids'] = result['fields']['child_ids']
                result['fields']['contact_ids'].update(
                    self.fields_get(['contact_ids'])['contact_ids'])
            result['arch'] = etree.tostring(doc)
        return result

    def get_view(self, view_id=None, view_type='form', **options):
        result = super(ResPartner, self).get_view(view_id, view_type, **options)
        node = etree.fromstring(result['arch'])
        view_fields = set(el.get('name') for el in node.xpath('.//field[not(ancestor::field)]'))
        result['fields'] = self.fields_get(view_fields)
        return self._update_fields_view_get_result(result, view_type)

    @api.model
    def _format_args(self, args):
        for cond in (args or []):
            if len(cond) == 3 and cond[2] and isinstance(cond[2], list) and \
                isinstance(cond[2][0], list):
                for index, item in enumerate(cond[2]):
                    if item[0] == 1:
                        cond[2][index] = item[1]
                    elif item[0] == 6:
                        cond[2] = item[2]
                        break

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        self._format_args(args)
        return super(ResPartner, self).name_search(name, args, operator, limit)

    def _search(self, args, offset=0, limit=None, order=None, count=False):
        self._format_args(args)
        if count:
            return super(ResPartner, self)._search(args, offset=offset, limit=limit, order=order, count=True)
        return super(ResPartner, self)._search(args, offset=offset, limit=limit, order=order)

