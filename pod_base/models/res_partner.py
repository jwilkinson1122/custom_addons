import logging
import base64
import json
from lxml import etree
from pytz import UTC
from datetime import datetime, time
from random import choice
from string import digits
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta
from markupsafe import Markup


from odoo import _, models, fields, tools, api, exceptions, Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.osv import expression
from odoo.osv.expression import FALSE_LEAF, OR, is_leaf
from odoo.tools.safe_eval import safe_eval
from odoo.tools import config, format_date


_logger = logging.getLogger(__name__)

INVOICE = "invoice"

class Partner(models.Model):
    _inherit = "res.partner"

    is_partner = fields.Boolean(string='Partner', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_location = fields.Boolean(string='Location', default=False)
    is_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_member = fields.Boolean(string="Member", tracking=True)
    customer = fields.Boolean(string='Is a Customer', default=True)
    supplier = fields.Boolean(string='Is a Vendor')


    patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_counts')
    patient_records = fields.One2many('pod.patient', compute='_compute_patient_records', string="Patients")
    patient_text = fields.Char(compute="_compute_patient_text")

    partner_id = fields.Many2one("res.partner", copy=False)
    # parent_id = fields.Many2one(ondelete='restrict')
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_company','=',True)], string="Account")
    location_id = fields.Many2one('res.partner', index=True, domain=[('is_location','=',True)], string="Location")
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    location_type_id = fields.Many2one(string='Type', comodel_name='pod.location.type')
    location_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Type', default='')
    
    # child_ids = fields.One2many('res.partner', 'parent_id', string='Contact', domain=[('active', '=', True)])

    child_ids = fields.One2many("res.partner", compute="_compute_practitioners", string="Practitioners", readonly=True)
    contact_ids = fields.One2many('res.partner', 'parent_id', 'Contacts & Addresses', domain=[('is_company', '=', False)])
    
    subcompanies_count = fields.Integer('Number of sub-companies', compute='_compute_subcompanies_count')
    subcompanies_label = fields.Char(related='partner_type_id.subcompanies_label', readonly=True)
    parent_relation_label = fields.Char(related='partner_type_id.parent_relation_label', readonly=True)
    # parent_relation_label = fields.Char('Relationship', translate=True, default='Attached To:', readonly=True)

    practitioner_id = fields.Many2one('res.partner', 'Practitioner', compute='_compute_practitioner', store=True, readonly=False)
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")

    type = fields.Selection(default=False)
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')
    
    partner_above_ids = fields.One2many(
        comodel_name='res.partner.relation.hierarchy',
        inverse_name='partner_id',
        string='Partners above in hierarchy',
        readonly=True)
    partner_above_hierarchy = fields.Char(
        string="Upper level partners",
        compute='_compute_partners_above',
        readonly=True)
    has_partner_above = fields.Boolean(
        compute='_compute_partners_above',
        readonly=True)
    
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
    parent_type_ids = fields.Many2many('res.partner.type', string='Company types authorized for parent', compute='_compute_parent_types')

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

    role_ids = fields.Many2many(
        string="Roles", 
        comodel_name="pod.role", 
        default=lambda self: [(6, 0, [])],  # This sets an empty list as the default value
    )

    role_required = fields.Boolean(
        compute='_compute_role_required', 
        inverse='_inverse_role_required', 
        string="Is Role Required", 
        store=False
        )
    
    fax = fields.Char(string="Fax", tracking=True)
    notes = fields.Text('Notes', groups="pod_contacts.group_user")
    additional_note = fields.Text(string='Additional Note', groups="pod_contacts.group_user", tracking=True)
    color = fields.Integer('Color Index', default=0)
    barcode = fields.Char(string="Badge ID", help="ID used for partner identification.", groups="pod_contacts.group_user", copy=False)
        
    ref = fields.Char(name="Reference", readonly=True, default="New", index=True)

    _sql_constraints = [('barcode_uniq', 'unique (barcode)', "The ID must be unique, this one is already assigned to another partner.")]
    
    # company_type = fields.Selection(
    # string='Company Type', 
    # selection=[
    #         ('company', 'Account'), 
    #         ('location', 'Location'), 
    #         ('person', 'Person')
    #         ], 
    # compute='_compute_company_type', 
    # inverse='_write_company_type', 
    # store=True
    #         )

    # Compute Methods
    # @api.depends('company_type')
    # def _compute_company_type(self):
    #     for record in self:
    #         field_mapping = {
    #             'company': ('is_company', False, False, False),
    #             'location': (False, 'is_location', False, False),
    #             'person': (False, False, record.is_practitioner, record.is_member),
    #         }
    #         fields_to_set = field_mapping.get(record.company_type, (False, False, False, False))
    #         record.is_company, record.is_location, record.is_practitioner, record.is_member = fields_to_set

    # def _write_company_type(self):
    #     for record in self:
    #         if record.is_company:
    #             record.company_type = 'company'
    #         elif record.is_location:
    #             record.company_type = 'location'
    #         elif any([record.is_practitioner, record.is_member]):
    #             record.company_type = 'person'
    #         else:
    #             pass

    def generate_random_barcode(self):
        for partner in self:
            partner.barcode = '041'+"".join(choice(digits) for i in range(9))

    @api.depends('name', 'partner_id.avatar_1920', 'image_1920')
    def _compute_avatar_1920(self):
        super()._compute_avatar_1920()

    @api.depends('name', 'partner_id.avatar_1024', 'image_1024')
    def _compute_avatar_1024(self):
        super()._compute_avatar_1024()

    @api.depends('name', 'partner_id.avatar_512', 'image_512')
    def _compute_avatar_512(self):
        super()._compute_avatar_512()

    @api.depends('name', 'partner_id.avatar_256', 'image_256')
    def _compute_avatar_256(self):
        super()._compute_avatar_256()

    @api.depends('name', 'partner_id.avatar_128', 'image_128')
    def _compute_avatar_128(self):
        super()._compute_avatar_128()

    def _compute_avatar(self, avatar_field, image_field):
        partners_with_internal_user = self.filtered(lambda partner: partner.user_ids - partner.user_ids.filtered('share'))
        super(Partner, partners_with_internal_user)._compute_avatar(avatar_field, image_field)
        partners_without_image = (self - partners_with_internal_user).filtered(lambda p: not p[image_field])
        for _, group in tools.groupby(partners_without_image, key=lambda p: p._avatar_get_placeholder_path()):
            group_partners = self.env['res.partner'].concat(*group)
            group_partners[avatar_field] = base64.b64encode(group_partners[0]._avatar_get_placeholder())

        for partner in self - partners_with_internal_user - partners_without_image:
            partner[avatar_field] = partner[image_field]

    def _avatar_get_placeholder_path(self):
        if self.type == 'delivery':
            return "base/static/img/truck.png"
        elif self.type == 'invoice':
            return "base/static/img/money.png"
        elif self.is_company or self.is_location:
            return "base/static/img/company_image.png"
        else:
            return super()._avatar_get_placeholder_path()
        
    def _compute_partners_above(self):
        """Check partners up in the hierarchy if any."""
        for rec in self:
            rec.partner_above_hierarchy = \
                rec.partner_above_ids and \
                rec.partner_above_ids[0].hierarchy_display or ''
            rec.has_partner_above = bool(rec.partner_above_ids)

    def is_above(self, other_partner):
        """Check whether this partner is above other_partner."""
        self.ensure_one()
        for partner_above in other_partner.partner_above_ids:
            if self.id == partner_above.partner_above_id.id:
                return True
        return False

    @api.depends('parent_id', 'is_company', 'active')
    def _compute_locations(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_locations = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", True), 
                    ("patient_ids", "=", False),  # Exclude records that have associated patients
                    ("active", "=", True)
                ])
                record.location_ids = all_locations - record
            else:
                record.location_ids = self.env['res.partner']  # Empty recordset
  
    @api.depends('location_count')
    def _compute_location_text(self):
        for record in self:
            if not record.location_count:
                record.location_text = False
            elif record.location_count == 1:
                record.location_text = _("(1 Location)")
            else:
                record.location_text = _("(%s Locations)" % record.location_count)

    @api.depends('is_practitioner', 'role_ids')
    def _compute_role_required(self):
        for record in self:
            record.role_required = record.is_practitioner and not record.role_ids

    def _inverse_role_required(self):
        for record in self:
            if record.role_required and not record.role_ids:
                raise ValidationError("Roles are required for practitioners.")

    @api.constrains('is_practitioner', 'role_ids')
    def _check_pod_practitioner_roles(self):
        for record in self:
            if record.is_practitioner and not record.role_ids:
                raise ValidationError(_("Roles are required for practitioners."))

    @api.depends('parent_id', 'is_company', 'is_practitioner', 'active')
    def _compute_practitioners(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_practitioners = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", False),
                    ("is_practitioner", "=", True),  
                    ("patient_ids", "=", False),  # Exclude records that have associated patients
                    ("active", "=", True)
                ])
                record.child_ids = all_practitioners
            else:
                record.child_ids = self.env['res.partner']  # Empty recordset 

    @api.depends('parent_id')
    def _compute_practitioner(self):
        for practitioner in self:
            manager = practitioner.parent_id
            previous_manager = practitioner._origin.parent_id
            if manager and (practitioner.practitioner_id == previous_manager or not practitioner.practitioner_id):
                practitioner.practitioner_id = manager
            elif not practitioner.practitioner_id:
                practitioner.practitioner_id = False

    @api.depends('practitioner_count')
    def _compute_practitioner_text(self):
        for record in self:
            if not record.practitioner_count:
                record.practitioner_text = False
            elif record.practitioner_count == 1:
                record.practitioner_text = _("(1 Practitioner)")
            else:
                record.practitioner_text = _("(%s Practitioners)" % record.practitioner_count)

    def action_open_practitioners(self):
        self.ensure_one()
        if len(self.child_ids) > 1:
            return {
                'name': _('Related Contacts'),
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'domain': [('id', 'in', self.child_ids.ids)],
            }
        return {
            'name': _('Contact'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.child_ids.id,
            'view_mode': 'form',
        }

    @api.depends('child_ids', 'child_ids.is_company')
    def _compute_location_and_practitioner_counts(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record

                locations = all_partners.filtered(lambda p: p.is_company)
                record.location_count = len(locations)

                # Adjusting the domain to exclude records related to patients
                practitioners = all_partners.filtered(lambda p: not p.is_company and not p.patient_ids)
                record.practitioner_count = len(practitioners)
            else:
                record.location_count = 0
                record.practitioner_count = 0
    
    @api.depends('child_ids', 'child_ids.patient_ids')
    def _compute_patient_counts(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.patient_count = 0  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                patients = all_partners.mapped('patient_ids')
                record.patient_count = len(patients)
            else:
                record.patient_count = 0

    @api.depends('child_ids', 'child_ids.patient_ids')
    def _compute_patient_records(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.patient_records = self.env['pod.patient']  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                record.patient_records = all_partners.mapped('patient_ids')
            else:
                record.patient_records = self.env['pod.patient']

    @api.depends('patient_count')
    def _compute_patient_text(self):
        for record in self:
            if not record.patient_count:
                record.patient_text = False
            elif record.patient_count == 1:
                record.patient_text = _("(1 Patient)")
            else:
                record.patient_text = _("(%s Patients)" % record.patient_count)

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
            code = 'SUPPLIER' if self.supplier else 'LOCATION'
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
    def _get_pod_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []
    
    def _get_next_ref(self, vals=None):
        parent_id = vals.get("parent_id")
        if parent_id:
            parent = self.browse(parent_id)
            parent_ref = parent.ref
            existing_refs = self.search_count([
                ("parent_id", "=", parent_id),
                ("ref", "like", f"{parent_ref}-%")
            ])
            next_index = existing_refs + 1
            return f"{parent_ref}-{next_index}"
        return self.env["ir.sequence"].next_by_code("res.partner") or "New"

    def _get_partner_type(self, vals):
        if 'partner_type_id' in vals:
            return self.env['res.partner.type'].browse(vals['partner_type_id'])
        return self.partner_type_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            partner_type = self._get_partner_type(vals)
            if not vals.get("ref") and self._needs_ref(vals=vals):
                vals["ref"] = self._get_next_ref(vals=vals)
            if vals.get('is_partner') or vals.get('patient_ids'):
                self.check_pod("create")
            vals.update(self._get_inherit_values(partner_type))
            new_partner = super().create(vals)
            new_partner._update_children(vals)
        return new_partner

    def copy(self, default=None):
        default = default or {}
        if self._needs_ref():
            default["ref"] = self._get_next_ref()
        return super(Partner, self).copy(default=default)

    def write(self, vals):
        partners_by_type = {}
        partner_type = self._get_partner_type(vals)
        if 'parent_id' in vals:
            for partner in self:
                partner_vals = vals.copy()
                if not partner_vals.get("ref") and partner._needs_ref(vals=partner_vals) and not partner.ref:
                    partner_vals["ref"] = partner._get_next_ref(vals=partner_vals)
                if partner.is_partner or partner.patient_ids:
                    partner.check_pod("write")
                partner_vals.update(self._get_inherit_values(partner_type))
                super(Partner, partner).write(partner_vals)
        else:
            partners_by_type[partner_type] = self
            partner_vals = vals.copy()
            if list(vals.keys()) != ['is_company']:  # To avoid an infinite loop
                partner_vals.update(self._get_inherit_values(partner_type, not_null=True))
            super(Partner, partners_by_type[partner_type]).write(partner_vals)
            self._update_children(vals)
        return True

    def _needs_ref(self, vals=None):
        if not vals and not self:  # pragma: no cover
            raise exceptions.UserError(
                _("Either field values or an id must be provided.")
            )
        fields_for_check = ["is_company", "parent_id"]
        vals_for_check = vals.copy() if vals else {}
        if self:
            for field in fields_for_check:
                if field not in vals_for_check:
                    vals_for_check[field] = self[field]
        return vals_for_check.get("is_company") or not vals_for_check.get("parent_id")

    @api.model
    def _commercial_fields(self):
        """
        Make the partner reference a field that is propagated
        to the partner's contacts
        """
        return super(Partner, self)._commercial_fields() + ["ref"]

    # def _commercial_sync_to_children(self):
    #     if self._context.get('synced_children'):
    #         return
    #     self = self.with_context(synced_children=True)
    #     for child in self.child_ids.filtered(lambda c: not c.is_company):
    #         child._commercial_sync_to_children()

    def _commercial_sync_to_children(self):
        # Check if the children have already been synchronized
        if self._context.get('synced_children'):
            return

        # Update child records here
        for child in self.child_ids.filtered(lambda c: not c.is_company):
            vals_to_sync = {}  # Define the values to sync from parent to child
            if self.is_company:
                # Specify which fields to sync when the parent is a company
                vals_to_sync['ref'] = self.ref

            # Update child with the values
            child.write(vals_to_sync)

            # Recursively call the method for child's children if needed
            child._commercial_sync_to_children()

        # Set the context to mark that children have been synchronized
        self = self.with_context(synced_children=True)

    # def _commercial_sync_to_children(self):
    #     """ Handle sync of commercial fields to descendants """
    #     commercial_partner = self.commercial_partner_id
    #     sync_vals = commercial_partner._update_fields_values(self._commercial_fields())
    #     sync_children = self.child_ids.filtered(lambda c: not c.is_company)
    #     for child in sync_children:
    #         child._commercial_sync_to_children()
    #     res = sync_children.write(sync_vals)
    #     sync_children._compute_commercial_partner()
    #     return res


    def unlink(self):
        for partner in self:
            if partner.is_partner or partner.sudo().patient_ids:
                partner.check_pod("unlink")
        return super().unlink()
    
    @api.model
    def default_pod_fields(self):
        fields = ["is_partner", "is_company", "is_location", "is_practitioner"]
        # If there's a need to add more fields from parent or other inheriting models, you can do rx here.
        return fields

    @api.constrains("is_location", "parent_id")
    def check_pod_location(self):
        test_condition = not config["test_enable"] or self.env.context.get("test_check_pod_location")
        if not test_condition:
            return
        for record in self:
            if record.is_location and not record.parent_id:
                raise ValidationError(_("Parent Company must be fullfilled on locations"))

    def check_pod(self, mode="write"):
        if self.env.su:
            return self._check_pod(mode=mode)

    def _check_pod(self, mode="write"):
        if self.sudo().patient_ids:
            self.sudo().patient_ids.check_access_rights(mode)
        
        checks = [
            (self.is_partner, self._check_pod_user, "pod_contacts.group_user"),
            (self.is_company, self._check_pod_account, "pod_contacts.group_configurator"),
            (self.is_practitioner, self._check_pod_practitioner, "pod_contacts.group_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_pod_user(self):
        return self.env.user.has_group("pod_contacts.group_user")
        
    def _check_pod_account(self):
        return self.env.user.has_group("pod_contacts.group_configurator")
        
    def _check_pod_practitioner(self):
        return self.env.user.has_group("pod_contacts.group_configurator")

    def open_parent(self):
        self.ensure_one()
        address_form_id = self.env.ref("base.view_partner_address_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [(address_form_id, "form")],
            "res_id": self.parent_id.id,
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }

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


    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the practitioners of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_pod_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result

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
        result = super().get_view(view_id, view_type, **options)
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
