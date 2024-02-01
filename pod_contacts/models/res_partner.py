import logging
import base64
from pytz import UTC
from datetime import datetime, time
from random import choice
from string import digits
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta
from markupsafe import Markup

from odoo import _, models, fields, tools, api, Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.osv import expression
from odoo.tools import config, format_date


_logger = logging.getLogger(__name__)

INVOICE = "invoice"

class Partner(models.Model):
    _inherit = "res.partner"
    # _inherit = ['res.partner', 'mail.thread.main.attachment', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']
    # _order = "internal_identifier,name"
    
    is_partner = fields.Boolean(string='Partner', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_company_parent = fields.Boolean(string='Parent Company', compute="_compute_is_company_parent", store="True", default=False)
    is_location = fields.Boolean(string='Location', default=False)
    is_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_member = fields.Boolean(string="Member", tracking=True)

    partner_id = fields.Many2one("res.partner", copy=False)
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_company','=',True)], string="Account")
    location_id = fields.Many2one('res.partner', index=True, domain=[('is_location','=',True)], string="Location")
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    # location_ids = fields.One2many(
    #     "res.partner",
    #     "parent_id",
    # string="Locations",
    # domain=[("active", "=", True), ("is_company", "=", True)],
    # )
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    location_type_id = fields.Many2one(string='Type', comodel_name='pod.location.type')
    location_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Type', default='')
    

    child_ids = fields.One2many("res.partner", compute="_compute_practitioners", string="Practitioners", readonly=True)
    # child_ids = fields.One2many(domain=[("active", "=", True), ("is_company", "=", False)])
    practitioner_id = fields.Many2one('res.partner', 'Practitioner', compute='_compute_practitioner', store=True, readonly=False)
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    # role_type_id = fields.Many2one("pod.role",string="Role Type", tracking=True)
    # role_ids = fields.Many2many(string="Roles", comodel_name="pod.role")

    role_ids = fields.Many2many( string="Roles", comodel_name="pod.role", default=lambda self: [(6, 0, [])],  # This sets an empty list as the default value
    )

    role_required = fields.Boolean(compute='_compute_role_required', inverse='_inverse_role_required', string="Is Role Required", store=False)
    
    # root_ancestor = fields.Many2one(comodel_name='res.partner', string='Root Ancestor', compute='_compute_root_ancestor', store=True, recursive=True)
    
    highest_parent_id = fields.Many2one(
        "res.partner", compute="_compute_highest_parent_id", store="True", string="Highest parent"
    )

    all_child_ids = fields.One2many( string='All Children of the highest parent company', comodel_name='res.partner', inverse_name='highest_parent_id',
    )

    invoice_parent_address = fields.Boolean()
    invoice_address_to_use_id = fields.Many2one(
        "res.partner",
        "Invoice address to use", store=True, readonly=False, domain="['|', '&', ('type', '=', 'invoice') ,('parent_id', '=', parent_id), ('id', '=', parent_id)]",
    )

    patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_counts')
    patient_records = fields.One2many('pod.patient', compute='_compute_patient_records', string="Patients")
    patient_text = fields.Char(compute="_compute_patient_text")

    fax = fields.Char(string="Fax", tracking=True)
    notes = fields.Text('Notes', groups="pod_contacts.group_pod_user")
    additional_note = fields.Text(string='Additional Note', groups="pod_contacts.group_pod_user", tracking=True)
    color = fields.Integer('Color Index', default=0)
    barcode = fields.Char(string="Badge ID", help="ID used for partner identification.", groups="pod_contacts.group_pod_user", copy=False)
    
    relation_label = fields.Char('Relationship', translate=True, default='Attached To:', readonly=True)
    
    internal_identifier = fields.Char(name="Identifier", help="The Unique Sequence no", readonly=True, default="New", copy=False)
 
    # complete_name = fields.Char(compute="_compute_complete_name", store=True)

    _sql_constraints = [
        ('barcode_uniq', 'unique (barcode)', "The ID must be unique, this one is already assigned to another partner."),
        # ("internal_identifier_uniq", "unique (internal_identifier)", "The company internal_identifier must be unique!")
                        ]
    

    # @api.depends("internal_identifier", "name")
    # def _compute_complete_name(self):
    #     for partner in self:
    #         if not partner.internal_identifier:
    #             partner.complete_name = partner.name
    #         else:
    #             partner.complete_name = "{} - {}".format(partner.internal_identifier, partner.name)

    # @api.model
    # def name_search(self, name, args=None, operator="ilike", limit=100):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = ["|", ("internal_identifier", operator, name), ("name", operator, name)]
    #     partner = self.search(domain + args, limit=limit)
    #     return partner.name_get()

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
        

    @api.onchange("invoice_parent_address")
    def _onchange_invoice_parent_address(self):
        if not any(child.type == "invoice" for child in self.parent_id.child_ids):
            self.invoice_address_to_use_id = self.parent_id
        else:
            self.invoice_address_to_use_id = False

    def _update_for_specific_invoice_address(self, res={}):
        if res.get(INVOICE, False):
            res[INVOICE] = self.commercial_partner_id.invoice_address_to_use_id.id

    def address_get(self, adr_pref=None):
        res = super().address_get(adr_pref)
        commercial_partner = self.commercial_partner_id
        invoice_parent_address = (
            commercial_partner.invoice_parent_address
            and commercial_partner.parent_id
        )
        if INVOICE in res and invoice_parent_address:
            if not self.commercial_partner_id.invoice_address_to_use_id:
                # this case is only if record still empty
                # even "required" managed on view
                res[INVOICE] = self.parent_id.address_get([INVOICE])[INVOICE]
            else:
                # normally, it shoud only use this case :
                # invoice_parent_address set to True,
                # invoice_address_to_use_id shoud not be empty
                self._update_for_specific_invoice_address(res)
        return res

    @api.onchange("parent_id")
    def _update_invoice_parent_address(self):
        if not self.parent_id:
            self.invoice_parent_address = False

    # @api.depends('parent_id', 'parent_id.root_ancestor')
    # def _compute_root_ancestor(self):
    #     for rec in self:
    #         rec.root_ancestor = rec.parent_id and rec.parent_id.root_ancestor or rec

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

    # Role Methods
    @api.depends('is_practitioner', 'role_ids')
    def _compute_role_required(self):
        for record in self:
            record.role_required = record.is_practitioner and not record.role_ids

    # Inverse method
    def _inverse_role_required(self):
        for record in self:
            if record.role_required and not record.role_ids:
                raise ValidationError("Roles are required for practitioners.")

    @api.constrains('is_practitioner', 'role_ids')
    def _check_pod_practitioner_roles(self):
        for record in self:
            if record.is_practitioner and not record.role_ids:
                raise ValidationError(_("Roles are required for practitioners."))
            
    @api.model
    def _get_pod_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []
    

    # @api.depends("name", "internal_identifier")
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "[%s]" % record.internal_identifier
    #         if record.name:
    #             name = "{} {}".format(name, record.name)
    #         result.append((record.id, name))
    #     return result

    # @api.model_create_multi
    # def create(self, vals_list):
    #     partners = super(Partner, self).create(vals_list)
    #     for partner in partners:
    #         if partner.is_partner or partner.patient_ids:
    #             partner.check_pod("create")
    #     return partners


    # @api.model
    # def create(self, vals):
    #     vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
    #     return super(ResPartner, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
    #     return super(Partner, self).create(vals)


    @api.model_create_multi
    def create(self, vals):
        vals_upd = vals.copy()
        if vals_upd.get("internal_identifier", "New") == "New":
            vals_upd["internal_identifier"] = self._get_internal_identifier(vals_upd)
        partners = super().create(vals_upd)
        for partner in partners:
            if partner.is_partner or partner.patient_ids:
                partner.check_pod("create")
        return partners
    
    @api.model
    def _get_internal_identifier(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or 'New'
        return super(Partner, self).create(vals)
    



    def _get_highest_parent(self, partner):
        while partner.parent_id:
            partner = partner.parent_id
        return partner

    @api.depends("company_type", "location_ids", "parent_id", "child_ids", )
    def _compute_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                rec.highest_parent_id = self._get_highest_parent(rec)
            elif not rec.parent_id and rec.company_type == "company":
                rec.highest_parent_id = rec.id
            else:
                rec.highest_parent_id = False

    @api.depends("company_type", "location_ids", "parent_id", "child_ids")
    def _compute_is_company_parent(self):
        for rec in self:
            is_company_parent = False
            if rec.company_type == "company" and \
                    rec.location_ids and not rec.parent_id:
                is_company_parent = True
            rec.is_company_parent = is_company_parent

    def compute_locations_highest_parent_id(self, locations):
        locations._compute_highest_parent_id()
        for sub_location in locations.location_ids:
            self.compute_locations_highest_parent_id(sub_location)

    def compute_childs_highest_parent_id(self, childs):
        childs._compute_highest_parent_id()
        for sub_childs in childs.location_ids:
            self.compute_locations_highest_parent_id(sub_childs)


    # def write(self, vals):
    #     res = super(Partner, self).write(vals)
    #     if 'parent_id' in vals:
    #         for record in self:
    #             self.compute_locations_highest_parent_id(record.location_ids)
    #             self.compute_childs_highest_parent_id(record.child_ids)
    #     return res
            

    # def write(self, vals):
    #     if "active" in vals and "skip_active_pop" not in self._context:
    #         archive = vals.pop("active")
    # super().write(vals=vals)
    #         partners = self.env["res.partner"]
    #         for partner in self:
    #             partners |= partner.with_context(active_test=False).search(
    #                 [("id", "child_of", partner.id)]
    #             )
    # partners.with_context(skip_active_pop=True).write({"active": archive})
    #     return super().write(vals=vals)
            
    def write(self, vals):
        result = super().write(vals)
        if 'parent_id' in vals:
            for record in self:
                self.compute_locations_highest_parent_id(record.location_ids)
                self.compute_childs_highest_parent_id(record.child_ids)
                if record.is_partner or record.patient_ids:
                    record.check_pod("write")
        return result
    
    # def write(self, vals):
    #     result = super().write(vals)
    #     for record in self:
    #         if record.is_partner or record.patient_ids:
    #             record.check_pod("write")
    #     return result
    
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
            (self.is_partner, self._check_pod_user, "pod_contacts.group_pod_user"),
            (self.is_company, self._check_pod_account, "pod_contacts.group_pod_configurator"),
            (self.is_practitioner, self._check_pod_practitioner, "pod_contacts.group_pod_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_pod_user(self):
        return self.env.user.has_group("pod_contacts.group_pod_user")
        
    def _check_pod_account(self):
        return self.env.user.has_group("pod_contacts.group_pod_configurator")
        
    def _check_pod_practitioner(self):
        return self.env.user.has_group("pod_contacts.group_pod_configurator")

    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the practitioners of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_pod_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result
    
    def open_parent(self):
        """Utility method used to add an "Open Parent" button in partner
        views"""
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