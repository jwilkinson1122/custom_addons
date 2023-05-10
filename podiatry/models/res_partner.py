# -*- coding: utf-8 -*-
import numbers
import base64
import json
from lxml import etree
from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.osv.expression import FALSE_LEAF, OR, is_leaf

import logging

logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    parent_id = fields.Many2one(ondelete='restrict')
     # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(
        domain=[("active", "=", True), ("is_company", "=", False)]
    )

    # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )
    
    type = fields.Selection(default=False)
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
    parent_type_ids = fields.Many2many(
        'res.partner.type', string='Company types authorized for parent',
        compute='_compute_parent_types')
    contact_ids = fields.One2many(
        'res.partner', 'parent_id', 'Contacts & Addresses',
        domain=[('is_company', '=', False)])
    subcompanies_count = fields.Integer(
        'Number of sub-companies', compute='_compute_subcompanies_count')
    subcompanies_label = fields.Char(
        related='partner_type_id.subcompanies_label', readonly=True)
    parent_relation_label = fields.Char(
        related='partner_type_id.parent_relation_label', readonly=True)
    customer = fields.Boolean(string='Is a Practice', default=True,
                              help="Check this box if this contact is a customer. It can be selected in sales orders.")
    supplier = fields.Boolean(string='Is a Vendor',
                              help="Check this box if this contact is a vendor. It can be selected in purchase orders.")
    
    is_practice = fields.Boolean('Practice')
    is_practitioner = fields.Boolean('Practitioner')
    is_patient = fields.Boolean(string='Patient')
    practice_id = fields.Many2one('res.partner', domain=[('is_company', '=', True), ('is_practice', '=', True)], string="Practice", required=True)
    practice_ids = fields.Many2many(comodel_name='res.partner', relation='practice_partners_rel', column1='practice_id', column2='partner_id', string="Practices")
    # practice_id = fields.Many2one('res.partner', domain=[('is_company', '=', True), ('is_practice', '=', True)], string="Practice", required=True)
    practitioner_id = fields.Many2one('res.partner', domain=[('is_company', '=', False), ('is_practitioner', '=', True)], string="Practitioner", required=True)
    practitioner_ids = fields.Many2many(comodel_name='res.partner', relation='practitioner_partners_rel', column1='practitioner_id', column2='partner_id', string="Practitioners")
    patient_ids = fields.One2many(comodel_name='podiatry.patient', inverse_name='practice_id', string="Patients")
    # practitioner_ids = fields.One2many(comodel_name='podiatry.practitioner', inverse_name='practice_id', string="Practice Contacts")
    # prescription_ids = fields.One2many(comodel_name='podiatry.prescription', inverse_name='practice_id', string="Prescriptions")
    prescription_ids = fields.One2many(comodel_name='podiatry.prescription', inverse_name='partner_id', string='Prescriptions')
    reference = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    notes = fields.Text(string="Notes")
    fax = fields.Char()
    practice_type = fields.Selection([('clinic', 'Clinic'),
                                      ('hospital', 'Hospital'),
                                      ('multi', 'Multi-Hospital'),
                                      ('military', 'Military Medical Center'),
                                      ('other', 'Other')],
                                     string="Practice Type")
    
    same_reference_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Practice with same Identity',
        compute='same_reference_partner_id',
    )
    
    @api.depends('reference')
    def same_reference_partner_id(self):
        for partner in self:
            domain = [
                ('reference', '=', partner.reference),
            ]

            origin_id = partner._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            partner.same_reference_partner_id = bool(partner.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)
    
    child_count = fields.Integer(
        string="Subpractice Count",
        compute='_compute_child_count',
    )
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        for partner in self:
            partner.child_count = len(partner.child_ids)
        return

    full_name = fields.Char(string="Full Name", compute='_compute_full_name', store=True)

    @api.depends('name', 'parent_id.full_name')
    def _compute_full_name(self):
        for practice in self:
            if practice.parent_id:
                practice.full_name = "%s / %s" % (
                    practice.parent_id.full_name, practice.name)
            else:
                practice.full_name = practice.name
        return
    
    @api.depends('partner_type_id')
    def _compute_parent_types(self):
        self.parent_type_ids = self.partner_type_id.parent_type_ids

    @api.depends('child_ids')
    def _compute_subcompanies_count(self):
        subcompanies = self.mapped('child_ids').filtered(
            lambda child: child.is_company)
        self.subcompanies_count = len(subcompanies)

    @api.depends('partner_type_id')
    def _compute_partner_type_infos(self):
        self.can_have_parent = True
        self.parent_is_required = False
        if self.partner_type_id:
            self.can_have_parent = self.partner_type_id.can_have_parent
            if self.partner_type_id.can_have_parent:
                self.parent_is_required = \
                    self.partner_type_id.parent_is_required

    @api.onchange('company_type')
    def _onchange_company_type(self):
        code = 'CONTACT'
        if self.company_type == 'company':
            code = 'SUPPLIER' if self.supplier else 'CLIENT'
        self.partner_type_id = self.partner_type_id.search(
            [('code', '=', code)], limit=1)

    @api.onchange('partner_type_id')
    def _onchange_partner_type(self):
        self.update(self._get_inherit_values(self.partner_type_id))

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
        partner_type = self.env['res.partner.type'].browse(vals.get('partner_type_id'))
        vals.update(self._get_inherit_values(partner_type))
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('podiatry.practice') or _('New')
            vals['reference'] = self.env['ir.sequence'].next_by_code('podiatry.practitioner') or _('New')
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

    def view_subcompanies(self):
        return {
            'name': _('Sub-companies'),
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

    @api.model
    def _search(
        self, args, offset=0, limit=None, order=None, count=False,
        access_rights_uid=None):
        self._format_args(args)
        return super(ResPartner, self)._search(
            args, offset, limit, order, count, access_rights_uid)
    
    def _get_display_name_context(self):
        self.ensure_one()
        partner = self.with_context(
            show_address=None, show_address_only=None, show_email=None)
        return {'partner': partner, '_': _}

    @api.depends('partner_type_id.partner_display_name')
    def _compute_display_name(self):
        rule = self.partner_type_id.partner_display_name
        if rule:
            self.display_name = safe_eval(
                rule, self._get_display_name_context())
        else:
            super(ResPartner, self)._compute_display_name()

    def action_open_prescriptions(self):
            return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.prescription',
            'domain': [('practice_id', '=', self.id)],
            'context': {'default_practice_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
            
    def action_open_patients(self):
            return {
            'type': 'ir.actions.act_window',
            'name': 'Patients',
            'res_model': 'podiatry.patient',
            'domain': [('practice_id', '=', self.id)],
            'context': {'default_practice_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
            
    def action_open_practitioners(self):
            return {
            'type': 'ir.actions.act_window',
            'name': 'Practitioners',
            'res_model': 'res.partner',
            'domain': [('practice_id', '=', self.id)],
            'context': {'default_practice_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
                 
class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Contact Type'
    _company_inherit_fields = ['company_type', 'customer', 'supplier']
    _person_inherit_fields = ['company_type', 'type']

    id = fields.Integer(readonly=True)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)  # Readonly if id
    sequence = fields.Integer('Priority', default=10)
    active = fields.Boolean(default=True)

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
    subcompanies_label = fields.Char(
        'Sub-companies label', translate=True, required=True,
        default='Sub-companies')

    # Inherited fields for partners of this type
    company_type = fields.Selection([
        ('person', 'Contact'),
        ('company', 'Practice'),
    ], 'Company Type', required=True, default='company')
    
    customer = fields.Boolean(
        string='Is a Pratice', default=True,
        help="Check this box if this contact is a practice.")
    
    supplier = fields.Boolean(
        string='Is a Vendor',
        help="Check this box if this contact is a vendor. "
        "If it's not checked, purchase people will not see it "
        "when encoding a purchase order.")
    
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

class PartnerCategory(models.Model):
    _inherit = "res.partner.category"

    partner_count = fields.Integer(
        string="Partners", compute="_compute_partner_count", store=False
    )

    @api.depends("partner_ids", "partner_ids.category_id")
    def _compute_partner_count(self):
        """Count Partners in category"""
        for rec in self:
            rec.partner_count = len(rec.partner_ids)

    def name_get(self):
        """Show Partner Count if required"""
        if not self._context.get("partner_count_display", False):
            return super(PartnerCategory, self).name_get()
        return [
            (category.id, "{} ({})".format(category.name, str(category.partner_count)))
            for category in self
        ]

class ResPartnerExtend(models.Model):
    """Extend partner with relations and allow to search for relations
    in various ways.
    """

    # pylint: disable=invalid-name
    # pylint: disable=no-member
    _inherit = "res.partner"

    relation_count = fields.Integer( string="Relation Count", compute="_compute_relation_count"
    )
    relation_all_ids = fields.One2many( comodel_name="res.partner.relation.all", inverse_name="this_partner_id", string="All relations with current partner", auto_join=True, search=False, copy=False,
    )
    search_relation_type_id = fields.Many2one( comodel_name="res.partner.relation.type.selection", compute=lambda self: self.update({"search_relation_type_id": None}), search="_search_relation_type_id", string="Has relation of type",
    )
    search_relation_partner_id = fields.Many2one( comodel_name="res.partner", compute=lambda self: self.update({"search_relation_partner_id": None}), search="_search_related_partner_id", string="Has relation with",
    )
    search_relation_date = fields.Date( compute=lambda self: self.update({"search_relation_date": None}), search="_search_relation_date", string="Relation valid",
    )
    search_relation_partner_category_id = fields.Many2one( comodel_name="res.partner.category", compute=lambda self: self.update({"search_relation_partner_category_id": None}), search="_search_related_partner_category_id", string="Has relation with a partner in category",
    )

    @api.depends("relation_all_ids")
    def _compute_relation_count(self):
        """Count the number of relations this partner has for Smart Button

        Don't count inactive relations.
        """
        for rec in self:
            rec.relation_count = len(rec.relation_all_ids.filtered("active"))

    @api.model
    def _search_relation_type_id(self, operator, value):
        """Search partners based on their type of relations."""
        result = []
        SUPPORTED_OPERATORS = (
            "=",
            "!=",
            "like",
            "not like",
            "ilike",
            "not ilike",
            "in",
            "not in",
        )
        if operator not in SUPPORTED_OPERATORS:
            raise exceptions.ValidationError(
                _('Unsupported search operator "%s"') % operator
            )
        type_selection_model = self.env["res.partner.relation.type.selection"]
        relation_type_selection = []
        if operator == "=" and isinstance(value, numbers.Integral):
            relation_type_selection += type_selection_model.browse(value)
        elif operator == "!=" and isinstance(value, numbers.Integral):
            relation_type_selection = type_selection_model.search(
                [("id", operator, value)]
            )
        else:
            relation_type_selection = type_selection_model.search(
                [
                    "|",
                    ("type_id.name", operator, value),
                    ("type_id.name_inverse", operator, value),
                ]
            )
        if not relation_type_selection:
            result = [FALSE_LEAF]
        for relation_type in relation_type_selection:
            result = OR(
                [
                    result,
                    [("relation_all_ids.type_selection_id.id", "=", relation_type.id)],
                ]
            )
        return result

    @api.model
    def _search_related_partner_id(self, operator, value):
        """Find partner based on relation with other partner."""
        # pylint: disable=no-self-use
        return [("relation_all_ids.other_partner_id", operator, value)]

    @api.model
    def _search_relation_date(self, operator, value):
        """Look only for relations valid at date of search."""
        # pylint: disable=no-self-use
        return [
            "&",
            "|",
            ("relation_all_ids.date_start", "=", False),
            ("relation_all_ids.date_start", "<=", value),
            "|",
            ("relation_all_ids.date_end", "=", False),
            ("relation_all_ids.date_end", ">=", value),
        ]

    @api.model
    def _search_related_partner_category_id(self, operator, value):
        """Search for partner related to a partner with search category."""
        # pylint: disable=no-self-use
        return [("relation_all_ids.other_partner_id.category_id", operator, value)]

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Inject searching for current relation date if we search for
        relation properties and no explicit date was given.
        """
        # pylint: disable=arguments-differ
        # pylint: disable=no-value-for-parameter
        date_args = []
        for arg in args:
            if (
                is_leaf(arg)
                and isinstance(arg[0], str)
                and arg[0].startswith("search_relation")
            ):
                if arg[0] == "search_relation_date":
                    date_args = []
                    break
                if not date_args:
                    date_args = [("search_relation_date", "=", fields.Date.today())]
        # because of auto_join, we have to do the active test by hand
        active_args = []
        if self.env.context.get("active_test", True):
            for arg in args:
                if (
                    is_leaf(arg)
                    and isinstance(arg[0], str)
                    and arg[0].startswith("search_relation")
                ):
                    active_args = [("relation_all_ids.active", "=", True)]
                    break
        return super(ResPartner, self).search(
            args + date_args + active_args, offset=offset, limit=limit, order=order, count=count,
        )

    def get_partner_type(self):
        """Get partner type for relation.
        :return: 'c' for company or 'p' for person
        :rtype: str
        """
        self.ensure_one()
        return "c" if self.is_company else "p"

    def action_view_relations(self):
        for contact in self:
            relation_model = self.env["res.partner.relation.all"]
            relation_ids = relation_model.search(
                [
                    "|",
                    ("this_partner_id", "=", contact.id),
                    ("other_partner_id", "=", contact.id),
                ]
            )
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "podiatry.action_res_partner_relation_all"
            )
            action["domain"] = [("id", "in", relation_ids.ids)]
            context = action.get("context", "{}").strip()[1:-1]
            elements = context.split(",") if context else []
            to_add = [
                """'search_default_this_partner_id': {0},
                        'default_this_partner_id': {0},
                        'active_model': 'res.partner',
                        'active_id': {0},
                        'active_ids': [{0}],
                        'active_test': False""".format(
                    contact.id
                )
            ]
            context = "{" + ", ".join(elements + to_add) + "}"
            action["context"] = context
            return action
