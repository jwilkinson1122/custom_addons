# -*- coding: utf-8 -*-
import json
import base64
import logging
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import _, models, fields, tools, api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools import config
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['pod.abstract', 'res.partner', 'mail.thread', 'mail.activity.mixin']

    # _inherit = ["pod.abstract", "mail.thread", "mail.activity.mixin"]
    # _inherits = {"res.partner": "partner_id"}

   # Identifier Booleans
    is_pod = fields.Boolean(string='Podiatry', default=False)
    is_company = fields.Boolean(string="Account", tracking=True)
    is_location = fields.Boolean(string="Location", tracking=True)
    is_practitioner = fields.Boolean(string="Practitioner", tracking=True)
    is_personnel = fields.Boolean(string="Personnel", tracking=True)
    is_patient = fields.Boolean('Patient', tracking=True)
    is_sales_partner = fields.Boolean(string="Sales Partner", tracking=True)

    
    partner_id = fields.Many2one("res.partner")
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Attached To:', readonly=True)
    
    # Account
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_company','=',True)], string="Account")
    
    # Locations
    # location_ids = fields.One2many(
    #     "res.partner", 
    #     compute="_compute_locations", 
    #     string="Locations", 
    #     readonly=True
    #     )
    
    location_ids = fields.One2many(
            "res.partner",
            "partner_id",
            string="Locations",
            domain=[("active", "=", True), ("is_location", "=", True)],
        )
    
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    location_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Location Type',
        default='clinic')

    # Practitioners
    # child_ids = fields.One2many(
    #     "res.partner", 
    #     compute="_compute_practitioners", 
    #     string="Practitioners", 
    #     readonly=True
    #     )
    
    child_ids = fields.One2many(
            "res.partner",
            "partner_id",
            string="Practitioners",
            domain=[("active", "=", True), ("is_practitioner", "=", True)],
        )
    
    practitioner_count = fields.Integer(
        string='Practitioner Count', 
        compute='_compute_location_and_practitioner_counts'
        )
    
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    
    # Patients
    # patient_ids = fields.One2many("res.partner", inverse_name="partner_id")
    patient_ids = fields.One2many(
            "res.partner",
            "partner_id",
            string="Patients",
            domain=[("active", "=", True), ("is_patient", "=", True)],
        )


    patient_records = fields.One2many('res.partner', compute='_compute_patient_records', string="Patients")
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_counts')
    patient_text = fields.Char(compute="_compute_patient_text")

    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", tracking=True)

    patient_birthday = fields.Date('Date of Birth', tracking=True)
    patient_birthday_str = fields.Char(string='Birthday string', compute='compute_patient_birthday_str', store=True)
    patient_url = fields.Char(string="Patient URL", tracking=True)
    
    @api.depends('patient_birthday')
    def compute_patient_birthday_str(self):
        for partner in self:
            partner.patient_birthday_str = partner.patient_birthday and partner.patient_birthday.strftime("%m/%d/%Y") or ""

    billing_id = fields.Many2one("res.partner", string="Billing", tracking=True)
    assistant_id = fields.Many2one("res.partner", string="Assistant", tracking=True)
    sales_partner_id = fields.Many2one("res.partner", string="Sales Partner", tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Default Warehouse", tracking=True)
    
    company_type = fields.Selection(string='Company Type', selection=[('company', 'Account'), ('location', 'Location'), ('person', 'Person')], compute='_compute_company_type', inverse='_write_company_type', store=True)
    # contact_type_id = fields.Many2one("contact.type",string="Contact Type", tracking=True)
    internal_identifier = fields.Char(string="Contact UUID", index=True)
    order_internal_code = fields.Char(string="Order UUID", index=True)
    record_num = fields.Char(string="Medical Record Number", tracking=True)
    program_group = fields.Char(string="Program Group", tracking=True)
    # program_ids = fields.Many2many("pod.program", "res_partner_program_rel", "partner_id", "program_id", string="Programs", tracking=True)
    # status_ids = fields.Many2one("pod.status", string="Status", tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    zip = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one('res.country.state', tracking=True)
    country_id = fields.Many2one('res.country', tracking=True)
    fax = fields.Char(string="Fax", tracking=True)


    @api.depends('company_type')
    def _compute_company_type(self):
        for record in self:
            field_mapping = {
                'company': ('is_company', False, False, False, False),
                'location': (False, 'is_location', False, False, False),
                'person': (False, False, record.is_practitioner, record.is_personnel, record.is_patient),
            }
            fields_to_set = field_mapping.get(record.company_type, (False, False, False, False, False))
            record.is_company, record.is_location, record.is_practitioner, record.is_personnel, record.is_patient = fields_to_set

    def _write_company_type(self):
        for record in self:
            if record.is_company:
                record.company_type = 'company'
            elif record.is_location:
                record.company_type = 'location'
            elif any([record.is_practitioner, record.is_personnel, record.is_patient]):
                record.company_type = 'person'
            else:
                # Handle the case where neither is selected, e.g., raise an error or set a default value.
                pass

    # _sql_constraints = [("internal_identifier_unique", "unique(internal_identifier)", 'Contact UUID Must be Unique!')]

    @api.depends('parent_id', 'is_company', 'is_location', 'active')
    def _compute_locations(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_locations = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", True), 
                    ("is_location", "=", True), 
                    ("patient_ids", "=", False),  
                    ("active", "=", True)
                ])
                record.location_ids = all_locations - record
            else:
                record.location_ids = self.env['res.partner'] 
  
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
            if not isinstance(record.id, models.NewId):
                all_practitioners = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", False),
                    ("is_location", "=", False),
                    ("is_practitioner", "=", True),  
                    ("active", "=", True)
                ])
                record.child_ids = all_practitioners
            else:
                record.child_ids = self.env['res.partner'] 
        
    @api.depends('practitioner_count')
    def _compute_practitioner_text(self):
        for record in self:
            if not record.practitioner_count:
                record.practitioner_text = False
            elif record.practitioner_count == 1:
                record.practitioner_text = _("(1 Practitioner)")
            else:
                record.practitioner_text = _("(%s Practitioners)" % record.practitioner_count)
      
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
    def _compute_patient_ids(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.patient_ids = self.env['res.partner']  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                record.patient_ids = all_partners.mapped('patient_ids')
            else:
                record.patient_ids = self.env['res.partner']

    @api.depends('patient_count')
    def _compute_patient_text(self):
        for record in self:
            if not record.patient_count:
                record.patient_text = False
            elif record.patient_count == 1:
                record.patient_text = _("(1 Patient)")
            else:
                record.patient_text = _("(%s Patients)" % record.patient_count)

    # @api.model
    # def _get_pod_identifiers(self):
    #     return []
    
    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("partner.internal.code")
            or "New"
        )
    
    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    # overriding this method to add the birthdate in display name
    # def _get_name(self):
    #     """ Utility method to allow name_get to be overrided without re-browse the partner """
    #     partner = self
    #     name = partner.name or ''
    #     if partner.patient_birthday and 'commit_assetsbundle' not in self._context:
    #         name += ' [' + partner.patient_birthday.strftime("%m/%d/%Y") + ']'
    #     if partner.company_name or partner.parent_id:
    #         if not name and partner.type in ['invoice', 'delivery', 'other']:
    #             name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
    #         if not partner.is_company and 'commit_assetsbundle' not in self._context:
    #             name = self._get_contact_name(partner, name)
    #     if self._context.get('show_address_only'):
    #         name = partner._display_address(without_company=True)
    #     if self._context.get('show_address'):
    #         name = name + "\n" + partner._display_address(without_company=True)
    #     name = name.replace('\n\n', '\n')
    #     name = name.replace('\n\n', '\n')
    #     if self._context.get('partner_show_db_id'):
    #         name = "%s (%s)" % (name, partner.id)
    #     if self._context.get('address_inline'):
    #         splitted_names = name.split("\n")
    #         name = ", ".join([n for n in splitted_names if n.strip()])
    #     if self._context.get('show_email') and partner.email:
    #         name = "%s<%s>" % (name, partner.email)
    #     if self._context.get('html_format'):
    #         name = name.replace('\n', '<br/>')
    #     if self._context.get('show_vat') and partner.vat:
    #         name = "%s ‒ %s" % (name, partner.vat)
    #     return name

    
    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner in partners:
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("create")
            # if not partner.get('internal_identifier'):
            #     partner['internal_identifier'] = self.env['ir.sequence'].next_by_code('partner.internal.code')
        return partners

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if not vals.get('internal_identifier'):
    #             vals['internal_identifier'] = self.env['ir.sequence'].next_by_code('partner.internal.code')
    #     return super().create(vals)

    def write(self, vals):
        result = super().write(vals)
        for partner in self:
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("write")
        return result

    def unlink(self):
        for partner in self:
            if partner.is_pod or partner.sudo().patient_ids:
                partner.check_pod("unlink")
        return super().unlink()
    
    @api.model
    def default_pod_fields(self):
        fields = ["is_pod", "is_company", "is_location", "is_practitioner", "is_patient"]
        # Add more fields from parent or other inheriting models here.
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
            (self.is_pod, self._check_pod_user, "pod_erp_base.group_pod_user"),
            (self.is_company, self._check_pod_account, "pod_erp_base.group_pod_configurator"),
            (self.is_location, self._check_pod_location, "pod_erp_base.group_pod_configurator"),
            (self.is_practitioner, self._check_pod_practitioner, "pod_erp_base.group_pod_configurator")
            (self.is_patient, self._check_pod_patient, "pod_erp_base.group_pod_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_pod_user(self):
        return self.env.user.has_group("pod_erp_base.group_pod_user")
        
    def _check_pod_account(self):
        return self.env.user.has_group("pod_erp_base.group_pod_configurator")
    
    def _check_pod_location(self):
        return self.env.user.has_group("pod_erp_base.group_pod_configurator")
        
    def _check_pod_practitioner(self):
        return self.env.user.has_group("pod_erp_base.group_pod_configurator")
    
    def _check_pod_patient(self):
        return self.env.user.has_group("pod_erp_base.group_pod_configurator")

    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the practitioners of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_pod_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result
    
 
    # def name_get(self):
    #     res = super(Partner, self).name_get()
    #     new_res = []
    #     for record in res:
    #         partner = self.browse(record[0])
    #         if partner.is_practitioner:
    #             name = partner.name
    #             new_res.append((partner.id, name))
    #         else:
    #             new_res.append(record)
    #     return new_res

    # overriding this method to add the birthdate in display name
    # def _get_name(self):
    #     """ Utility method to allow name_get to be overrided without re-browse the partner """
    #     partner = self
    #     name = partner.name or ''
    #     if partner.patient_birthday and 'commit_assetsbundle' not in self._context:
    #         name += ' [' + partner.patient_birthday.strftime("%m/%d/%Y") + ']'
    #     if partner.company_name or partner.parent_id:
    #         if not name and partner.type in ['invoice', 'delivery', 'other']:
    #             name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
    #         if not partner.is_company and 'commit_assetsbundle' not in self._context:
    #             name = self._get_contact_name(partner, name)
    #     if self._context.get('show_address_only'):
    #         name = partner._display_address(without_company=True)
    #     if self._context.get('show_address'):
    #         name = name + "\n" + partner._display_address(without_company=True)
    #     name = name.replace('\n\n', '\n')
    #     name = name.replace('\n\n', '\n')
    #     if self._context.get('partner_show_db_id'):
    #         name = "%s (%s)" % (name, partner.id)
    #     if self._context.get('address_inline'):
    #         splitted_names = name.split("\n")
    #         name = ", ".join([n for n in splitted_names if n.strip()])
    #     if self._context.get('show_email') and partner.email:
    #         name = "%s<%s>" % (name, partner.email)
    #     if self._context.get('html_format'):
    #         name = name.replace('\n', '<br/>')
    #     if self._context.get('show_vat') and partner.vat:
    #         name = "%s ‒ %s" % (name, partner.vat)
    #     return name


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
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(ResPartner, self).fields_view_get(view_id=view_id,
    # view_type=view_type,
    # toolbar=toolbar,
    # submenu=submenu)
    #
    #     if self.env.user.has_group('pod_erp_base.group_patient_editable'):
    #         doc = etree.XML(res['arch'])
    #         for field in res['fields']:
    #             for node in doc.xpath("//field[@name='location_ids'] \
    #                                 | //field[@name='child_ids'] \
    #                                 | //field[@name='assistant_id'] \
    #                                 | //field[@name='parent_id'] \
    #                                 | //field[@name='billing_id'] \
    #                                 | //field[@name='sales_partner_id']"):
    #                 node.set("readonly", "0")
    #                 modifiers = json.loads(node.get("modifiers"))
    #                 modifiers['readonly'] = False
    #                 node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc)
    #     return res

