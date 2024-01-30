import base64
import logging
from dateutil.relativedelta import relativedelta

from odoo import _, models, fields, tools, api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools import config

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "res.partner"
    # _inherit = ['pod.abstract', 'res.partner']
    # _inherit = ['pod.abstract', 'res.partner', 'mail.thread', 'mail.activity.mixin']
    # _inherit = ["pod.abstract", "mail.thread", "mail.activity.mixin"]
    # _inherits = {"res.partner": "partner_id"}


    is_partner = fields.Boolean(string='Partner', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_location = fields.Boolean(string='Location', default=False)
    is_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_personnel = fields.Boolean(string="Personnel", tracking=True)

    partner_id = fields.Many2one("res.partner")
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_company','=',True)], string="Account")
    
    # pod_location_id = fields.Many2one('res.partner', 'Location')
    pod_location_id = fields.Many2one('res.partner', index=True, domain=[('is_location','=',True)], string="Location")
    
    # pod_location_id = fields.Many2one(
    #     'res.partner', string='Location', check_company=True, index=True, tracking=True, compute='_compute_location_id', ondelete="set null", readonly=False, store=True, precompute=True)
    pod_location_ids = fields.One2many("res.partner", compute="_compute_pod_locations", string="Locations", readonly=True)
    # pod_location_ids = fields.Many2many('res.partner', string='Locations')

    
    pod_location_count = fields.Integer(string='Location Count', compute='_compute_pod_location_and_pod_practitioner_counts')
    pod_location_text = fields.Char(compute="_compute_pod_location_text")
    pod_location_type_id = fields.Many2one(string='Location Type', comodel_name='pod.location.type')
    pod_location_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Location Type', default='clinic')
    child_ids = fields.One2many("res.partner", compute="_compute_pod_practitioners", string="Practitioners", readonly=True)
    pod_practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_pod_location_and_pod_practitioner_counts')
    pod_practitioner_text = fields.Char(compute="_compute_pod_practitioner_text")
    pod_role_ids = fields.Many2many(string="Roles", comodel_name="pod.role")
    pod_role_required = fields.Boolean(compute='_compute_pod_role_required', inverse='_inverse_pod_role_required', string="Is Role Required", store=False)
    pod_patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")
    pod_patient_count = fields.Integer(string='Patient Count', compute='_compute_pod_patient_counts')
    pod_patient_records = fields.One2many('pod.patient', compute='_compute_pod_patient_records', string="Patients")
    pod_patient_text = fields.Char(compute="_compute_pod_patient_text")
    
    relation_label = fields.Char('Relationship', translate=True, default='Attached To:', readonly=True)
    pod_internal_identifier = fields.Char(
        name="Identifier", 
        help="Internal identifier used to identify this record", 
        readonly=True, 
        default="New", 
        copy=False,
    ) 
    # pod_contact_ids = fields.One2many("pod.contact", inverse_name="partner_id")
    # pod_contact_count = fields.Integer(compute="_compute_pod_contact_count")
    fax = fields.Char(string="Fax", tracking=True)
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
    #             'person': (False, False, record.is_practitioner, record.is_personnel),
    #         }
    #         fields_to_set = field_mapping.get(record.company_type, (False, False, False, False))
    #         record.is_company, record.is_location, record.is_practitioner, record.is_personnel = fields_to_set

    # def _write_company_type(self):
    #     for record in self:
    #         if record.is_company:
    #             record.company_type = 'company'
    #         elif record.is_location:
    #             record.company_type = 'location'
    #         elif any([record.is_practitioner, record.is_personnel]):
    #             record.company_type = 'person'
    #         else:
    #             pass

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
        
    # @api.depends("pod_contact_ids")
    # def _compute_pod_contact_count(self):
    #     for rec in self:
    #         rec.pod_contact_count = len(rec.pod_contact_ids.ids)

    # def action_view_pod_contacts(self):
    #     self.ensure_one()
    #     result = self.env["ir.actions.act_window"]._for_xml_id("pod_contacts.pod_contact_action")
    #     result["context"] = {"default_partner_id": self.id}
    #     result["domain"] = "[('partner_id', '=', " + str(self.id) + ")]"
    #     if len(self.pod_contact_ids) == 1:
    #         res = self.env.ref("pod.contact.view.form", False)
    #         result["views"] = [(res and res.id or False, "form")]
    #         result["res_id"] = self.pod_contact_ids.id
    #     return result



    @api.depends('parent_id', 'is_company', 'active')
    def _compute_pod_locations(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_locations = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", True), 
                    ("pod_patient_ids", "=", False),  # Exclude records that have associated patients
                    ("active", "=", True)
                ])
                record.pod_location_ids = all_locations - record
            else:
                record.pod_location_ids = self.env['res.partner']  # Empty recordset
  
    @api.depends('pod_location_count')
    def _compute_pod_location_text(self):
        for record in self:
            if not record.pod_location_count:
                record.pod_location_text = False
            elif record.pod_location_count == 1:
                record.pod_location_text = _("(1 Location)")
            else:
                record.pod_location_text = _("(%s Locations)" % record.pod_location_count)

    @api.depends('parent_id', 'is_company', 'is_practitioner', 'active')
    def _compute_pod_practitioners(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_practitioners = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", False),
                    ("is_practitioner", "=", True),  
                    ("pod_patient_ids", "=", False),  # Exclude records that have associated patients
                    ("active", "=", True)
                ])
                record.child_ids = all_practitioners
            else:
                record.child_ids = self.env['res.partner']  # Empty recordset 
        
    @api.depends('pod_practitioner_count')
    def _compute_pod_practitioner_text(self):
        for record in self:
            if not record.pod_practitioner_count:
                record.pod_practitioner_text = False
            elif record.pod_practitioner_count == 1:
                record.pod_practitioner_text = _("(1 Practitioner)")
            else:
                record.pod_practitioner_text = _("(%s Practitioners)" % record.pod_practitioner_count)
      
    @api.depends('child_ids', 'child_ids.is_company')
    def _compute_pod_location_and_pod_practitioner_counts(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record

                locations = all_partners.filtered(lambda p: p.is_company)
                record.pod_location_count = len(locations)

                # Adjusting the domain to exclude records related to patients
                practitioners = all_partners.filtered(lambda p: not p.is_company and not p.pod_patient_ids)
                record.pod_practitioner_count = len(practitioners)
            else:
                record.pod_location_count = 0
                record.pod_practitioner_count = 0
    
    @api.depends('child_ids', 'child_ids.pod_patient_ids')
    def _compute_pod_patient_counts(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.pod_patient_count = 0  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                patients = all_partners.mapped('pod_patient_ids')
                record.pod_patient_count = len(patients)
            else:
                record.pod_patient_count = 0

    @api.depends('child_ids', 'child_ids.pod_patient_ids')
    def _compute_pod_patient_records(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.pod_patient_records = self.env['pod.patient']  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                record.pod_patient_records = all_partners.mapped('pod_patient_ids')
            else:
                record.pod_patient_records = self.env['pod.patient']

    @api.depends('pod_patient_count')
    def _compute_pod_patient_text(self):
        for record in self:
            if not record.pod_patient_count:
                record.pod_patient_text = False
            elif record.pod_patient_count == 1:
                record.pod_patient_text = _("(1 Patient)")
            else:
                record.pod_patient_text = _("(%s Patients)" % record.pod_patient_count)

    # Role Methods
    @api.depends('is_practitioner', 'pod_role_ids')
    def _compute_pod_role_required(self):
        for record in self:
            record.pod_role_required = record.is_practitioner and not record.pod_role_ids

    # Inverse method
    def _inverse_pod_role_required(self):
        for record in self:
            if record.pod_role_required and not record.pod_role_ids:
                raise ValidationError("Roles are required for practitioners.")

    @api.constrains('is_practitioner', 'pod_role_ids')
    def _check_pod_practitioner_roles(self):
        for record in self:
            if record.is_practitioner and not record.pod_role_ids:
                raise ValidationError(_("Roles are required for practitioners."))
    
    @api.model
    def _get_pod_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []
    
    # @api.model
    # def _get_pod_internal_identifier(self, vals):
    #     return self.env["ir.sequence"].next_by_code("pod.contact") or "New"

    # @api.depends("name", "pod_internal_identifier")
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = "[%s]" % record.pod_internal_identifier
    #         if record.name:
    #             name = "{} {}".format(name, record.name)
    #         result.append((record.id, name))
    #     return result

    # @api.depends("active_date")
    # def _compute_active(self):
    #     for rec in self:
    #         rec.active = not bool(rec.active_date)

    # def close(self):
    #     return self.write(
    #         {
    #             "active_date": fields.Datetime.now(),
    #             "active_uid": self.env.user.id,
    #         }
    #     )
    
    @api.model_create_multi
    def create(self, vals):
        vals_upd = vals.copy()
        if vals_upd.get("pod_internal_identifier", "New") == "New":
            vals_upd["pod_internal_identifier"] = self._get_pod_internal_identifier(vals_upd)
        partners = super().create(vals_upd)
        for partner in partners:
            if partner.is_partner or partner.pod_patient_ids:
                partner.check_pod("create")
        return partners
    
    # @api.model
    # def create(self, vals_list):
    #     vals_upd = vals_list.copy()
    #     if vals_upd.get("pod_internal_identifier", "New") == "New":
    #         vals_upd["pod_internal_identifier"] = self._get_pod_internal_identifier(vals_upd)
    #         return super().create(vals_upd)
 
    def _get_pod_internal_identifier(self, vals):
        # It should be rewritten for each element
        raise UserError(_("Function is not defined"))

    def write(self, vals):
        result = super().write(vals)
        for partner in self:
            if partner.is_partner or partner.pod_patient_ids:
                partner.check_pod("write")
        return result

    def unlink(self):
        for partner in self:
            if partner.is_partner or partner.sudo().pod_patient_ids:
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
        if self.sudo().pod_patient_ids:
            self.sudo().pod_patient_ids.check_access_rights(mode)
        
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