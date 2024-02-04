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
    
    is_pod = fields.Boolean(string='Podiatry', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_pod_location = fields.Boolean(string='Location', default=False)
    is_pod_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_role_required = fields.Boolean(compute='_compute_is_role_required', inverse='_inverse_is_role_required', string="Is Role Required", store=False)
    # is_parent_practice = fields.Boolean( string='Parent Practice', related='parent_id.is_company', readonly=True, store=False)
    
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    practice_type_id = fields.Many2one(string='Practice Type', comodel_name='pod.practice.type')
    practice_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Practice Type',
        default='clinic')
    
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Attached To:', readonly=True)
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_company','=',True)], string="Practice")
    child_ids = fields.One2many("res.partner", compute="_compute_practitioners", string="Practitioners", readonly=True)

    practitioner_role_ids = fields.Many2many(string="Roles", comodel_name="pod.role")
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_counts')
    patient_records = fields.One2many('pod.patient', compute='_compute_patient_records', string="Patients")
    patient_text = fields.Char(compute="_compute_patient_text")

    # Compute Methods
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
        elif self.is_company or self.is_pod_location:
            return "base/static/img/company_image.png"
        else:
            return super()._avatar_get_placeholder_path()

    
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

    @api.depends('parent_id', 'is_company', 'is_pod_practitioner', 'active')
    def _compute_practitioners(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_practitioners = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", False),
                    ("is_pod_practitioner", "=", True),  
                    ("patient_ids", "=", False),  # Exclude records that have associated patients
                    ("active", "=", True)
                ])
                record.child_ids = all_practitioners
            else:
                record.child_ids = self.env['res.partner']  # Empty recordset 
        
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

            if record.is_pod_practitioner or record.is_company:
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

            if record.is_pod_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                record.patient_records = all_partners.mapped('patient_ids')
            else:
                record.patient_records = self.env['pod.patient']

    # def action_show_patients(self):
    #         self.ensure_one()
    #         action = {
    #             'name': _('Patients'),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'pod.patient',  
    #             'view_mode': 'tree,form',
    #             'domain': [('partner_id', '=', self.id)],
    #             'context': {'default_partner_id': self.id},
    #         }
    #         return action
        
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
    @api.depends('is_pod_practitioner', 'practitioner_role_ids')
    def _compute_is_role_required(self):
        for record in self:
            record.is_role_required = record.is_pod_practitioner and not record.practitioner_role_ids

    # Inverse method
    def _inverse_is_role_required(self):
        for record in self:
            if record.is_role_required and not record.practitioner_role_ids:
                raise ValidationError("Roles are required for practitioners.")

    @api.constrains('is_pod_practitioner', 'practitioner_role_ids')
    def _check_practitioner_roles(self):
        for record in self:
            if record.is_pod_practitioner and not record.practitioner_role_ids:
                raise ValidationError(_("Roles are required for practitioners."))
    
    @api.model
    def _get_pod_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner in partners:
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("create")
        return partners

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
        fields = ["is_pod", "is_company", "is_pod_location", "is_pod_practitioner"]
        # If there's a need to add more fields from parent or other inheriting models, you can do rx here.
        return fields

    @api.constrains("is_pod_location", "parent_id")
    def check_location_practice(self):
        test_condition = not config["test_enable"] or self.env.context.get("test_check_location_practice")
        if not test_condition:
            return
        for record in self:
            if record.is_pod_location and not record.parent_id:
                raise ValidationError(_("Parent Company must be fullfilled on locations"))

    def check_pod(self, mode="write"):
        if self.env.su:
            return self._check_pod(mode=mode)

    def _check_pod(self, mode="write"):
        if self.sudo().patient_ids:
            self.sudo().patient_ids.check_access_rights(mode)
        
        checks = [
            (self.is_pod, self._check_pod_user, "pod_prescriptions_contact.group_user"),
            (self.is_company, self._check_pod_practice, "pod_prescriptions_contact.group_configurator"),
            (self.is_pod_practitioner, self._check_pod_practitioner, "pod_prescriptions_contact.group_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_pod_user(self):
        return self.env.user.has_group("pod_prescriptions_contact.group_user")
        
    def _check_pod_practice(self):
        return self.env.user.has_group("pod_prescriptions_contact.group_configurator")
        
    def _check_pod_practitioner(self):
        return self.env.user.has_group("pod_prescriptions_contact.group_configurator")

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
    #         if partner.is_pod_practitioner:
    #             name = partner.name
    #             new_res.append((partner.id, name))
    #         else:
    #             new_res.append(record)
    #     return new_res

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