import numbers
import json
from lxml import etree

from odoo import _, api, exceptions, fields, models
from odoo.osv.expression import FALSE_LEAF, OR, is_leaf
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Company Identifier Booleans
    # is_company = fields.Boolean(string="Account", tracking=True)
    # is_location = fields.Boolean(string="Location", tracking=True)
    # is_practitioner = fields.Boolean(string="Practitioner", tracking=True)
    # is_patient = fields.Boolean('Patient', tracking=True)

    customer = fields.Boolean(string='Is a Customer', default=True, help="Check this box if this contact is a customer. It can be selected in sales orders.")
    supplier = fields.Boolean(string='Is a Vendor', help="Check this box if this contact is a vendor. It can be selected in purchase orders.")

    parent_id = fields.Many2one(ondelete='restrict')
    type = fields.Selection(default=False)
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
    parent_type_ids = fields.Many2many('res.partner.type', string='Company types authorized for parent', compute='_compute_parent_types')
  
    # force "active_test" domain to bypass _search() override
    # child_ids = fields.One2many(
    #     domain=[("active", "=", True), ("is_company", "=", False)]
    # )
    contact_ids = fields.One2many('res.partner', 'parent_id', 'Contacts', domain=[('is_company', '=', False)])
     # force "active_test" domain to bypass _search() override
    # affiliate_ids = fields.One2many(
    #     "res.partner",
    #     "parent_id",
    #     string="Affiliates",
    #     domain=[("active", "=", True), ("is_company", "=", True)],
    # )
    
    subcompanies_count = fields.Integer('Number of sub-companies', compute='_compute_subcompanies_count')
    subcompanies_label = fields.Char(related='partner_type_id.subcompanies_label', readonly=True)
    parent_relation_label = fields.Char(related='partner_type_id.parent_relation_label', readonly=True)
    relation_count = fields.Integer(compute="_compute_relation_count")
    relation_all_ids = fields.One2many(
        comodel_name="res.partner.relation.all",
        inverse_name="this_partner_id",
        string="All relations with current partner",
        auto_join=True,
        search=False,
        copy=False,
    )
    search_relation_type_id = fields.Many2one(
        comodel_name="res.partner.relation.type.selection",
        compute=lambda self: self.update({"search_relation_type_id": None}),
        search="_search_relation_type_id",
        string="Has relation of type",
    )
    search_relation_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute=lambda self: self.update({"search_relation_partner_id": None}),
        search="_search_related_partner_id",
        string="Has relation with",
    )
    search_relation_date = fields.Date(
        compute=lambda self: self.update({"search_relation_date": None}),
        search="_search_relation_date",
        string="Relation valid",
    )
    search_relation_partner_category_id = fields.Many2one(
        comodel_name="res.partner.category",
        compute=lambda self: self.update({"search_relation_partner_category_id": None}),
        search="_search_related_partner_category_id",
        string="Has relation with a partner in category",
    )

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

    # @api.depends('company_type')
    # def _compute_company_type(self):
    #     for record in self:
    #         field_mapping = {
    #             'company': ('is_company', False, False, False),
    #             'location': (False, 'is_location', False, False),
    #             'person': (False, False, record.is_practitioner, record.is_patient),
    #         }
    #         fields_to_set = field_mapping.get(record.company_type, (False, False, False, False))
    #         record.is_company, record.is_location, record.is_practitioner, record.is_patient = fields_to_set

    # def _write_company_type(self):
    #     for record in self:
    #         if record.is_company:
    #             record.company_type = 'company'
    #         elif record.is_location:
    #             record.company_type = 'location'
    #         elif any([record.is_practitioner, record.is_patient]):
    #             record.company_type = 'person'
    #         else:
    #             pass
                
    @api.onchange('company_type')
    def _onchange_company_type(self):
        code = 'CONTACT'
        if self.company_type == 'company':
            code = 'SUPPLIER' if self.supplier else 'CLIENT'
        self.partner_type_id = self.partner_type_id.search(
            [('code', '=', code)], limit=1)
 
    # @api.onchange('company_type')
    # def _onchange_company_type(self):
    #     code = 'CONTACT'
    #     for record in self:
    #         if record.company_type == 'company':
    #             if self.is_company:
    #                 code == 'ACCOUNT'    
    #         if record.company_type == 'location':
    #             if self.is_location:
    #                 code == 'LOCATION'    
    #         if record.company_type == 'person':    
    #             if self.is_practitioner:
    #                 code == 'PRACTITIONER'
    #             if self.is_patient:
    #                 code == 'PATIENT'     
    #         else:
    #             pass
            
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
        partner_type = self.env['res.partner.type'].browse(
            vals.get('partner_type_id'))
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

    def action_view_subcompanies(self):
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

    # def _update_fields_view_get_result(self, result, view_type='form'):
    #     if view_type == 'form' and not self._context.get(
    #         'display_original_view'):
    #         doc = etree.XML(result['arch'])
    #         for node in doc.xpath("//field[@name='child_ids']"):
    #             node.set('name', 'contact_ids')
    #             node.set('modifiers', json.dumps(
    #                 {   'default_is_company': False,
    #                     'default_is_location': False, 
    #                     'default_is_practitioner': False,
    #                     'default_is_patient': False,
    #                     }))
    #             result['fields']['contact_ids'] = result['fields']['child_ids']
    #             result['fields']['contact_ids'].update(
    #                 self.fields_get(['contact_ids'])['contact_ids'])
    #         result['arch'] = etree.tostring(doc)
    #     return result
    
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

    @api.depends("relation_all_ids")
    def _compute_relation_count(self):
        """Count the number of relations this partner has for Smart Button. Don't count inactive relations."""
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

# partners = self.env['res.partner'].search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        """Inject searching for current relation date if we search for
        relation properties and no explicit date was given.
        """
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
        return super().search(args + date_args + active_args, offset=offset, limit=limit, order=order)

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
                "pod_partner_multi_relation.action_res_partner_relation_all"
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
