import base64
import logging
from dateutil.relativedelta import relativedelta

from odoo import _, models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools import config

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "res.partner"
    
    is_pod = fields.Boolean(string='Podiatry', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_location = fields.Boolean(string='Location', default=False)
    is_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_role_required = fields.Boolean(compute='_compute_is_role_required', inverse='_inverse_is_role_required', string="Is Role Required", store=False)
    is_parent_practice = fields.Boolean( string='Parent Practice', related='parent_id.is_company', readonly=True, store=False)
    
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    
    practice_type_id = fields.Many2one(string='Practice Type', comodel_name='pod.practice.type')
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Attached To:', readonly=True)
    

    child_ids = fields.One2many("res.partner", compute="_compute_practitioners", string="Practitioners", readonly=True)
    practitioner_role_ids = fields.Many2many(string="Roles", comodel_name="pod.role")
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    
    patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")
    
    # practice_flag_ids = fields.One2many("pod.flag", inverse_name="practice_id")
    # practice_flag_count = fields.Integer(compute="_compute_partner_flag_count")
    # practitioner_flag_ids = fields.One2many("pod.flag", inverse_name="practitioner_id")
    # practitioner_flag_count = fields.Integer(compute="_compute_partner_flag_count")

    # Flag Methods
    # @api.depends("practice_flag_ids", "practitioner_flag_ids")
    # def _compute_partner_flag_count(self):
    #     for rec in self:
    #         rec.practice_flag_count = len(rec.practice_flag_ids.ids)
    #         rec.practitioner_flag_count = len(rec.practitioner_flag_ids.ids)

    # def _get_action_partner_view_flags(self, flag_field, context_key):
    #     self.ensure_one()
    #     result = self.env["ir.actions.act_window"]._for_xml_id("pod_base.pod_flag_action")
    #     result["context"] = {context_key: self.id}
    #     result["domain"] = "[('{}', '=', {})]".format(flag_field, self.id)
        
    #     flags = getattr(self, flag_field)
    #     if len(flags) == 1:
    #         res = self.env.ref("pod.flag.view.form", False)
    #         result["views"] = [(res and res.id or False, "form")]
    #         result["res_id"] = flags.id
    #     return result

    # def action_view_practice_flags(self):
    #     return self._get_action_partner_view_flags("practice_flag_ids", "default_practice_id")

    # def action_view_practitioner_flags(self):
    #     return self._get_action_partner_view_flags("practitioner_flag_ids", "default_practitioner_id")
        
              
    # Role Methods
    @api.depends('is_practitioner', 'practitioner_role_ids')
    def _compute_is_role_required(self):
        for record in self:
            record.is_role_required = record.is_practitioner and not record.practitioner_role_ids

    # Inverse method
    def _inverse_is_role_required(self):
        for record in self:
            if record.is_role_required and not record.practitioner_role_ids:
                raise ValidationError("Roles are required for practitioners.")

    @api.constrains('is_practitioner', 'practitioner_role_ids')
    def _check_practitioner_roles(self):
        for record in self:
            if record.is_practitioner and not record.practitioner_role_ids:
                raise ValidationError(_("Roles are required for practitioners."))
        
    @api.depends('parent_id', 'is_company', 'active')
    def _compute_locations(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_locations = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", True), 
                    ("active", "=", True)
                ])
                record.location_ids = all_locations - record
            else:
                record.location_ids = self.env['res.partner']  # Empty recordset
                

    # Compute Methods
    @api.depends('parent_id', 'is_company', 'is_practitioner', 'active')
    def _compute_practitioners(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_practitioners = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", False),
                    ("is_practitioner", "=", True),  
                    ("active", "=", True)
                ])
                record.child_ids = all_practitioners
            else:
                record.child_ids = self.env['res.partner']  # Empty recordset
  
  
    @api.depends('child_ids', 'child_ids.is_company')
    def _compute_location_and_practitioner_counts(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record

                locations = all_partners.filtered(lambda p: p.is_company)
                record.location_count = len(locations)

                practitioners = all_partners.filtered(lambda p: not p.is_company)
                record.practitioner_count = len(practitioners)
            else:
                record.location_count = 0
                record.practitioner_count = 0
                
    @api.depends('location_count')
    def _compute_location_text(self):
        for record in self:
            if not record.location_count:
                record.location_text = False
            elif record.location_count == 1:
                record.location_text = _("(1 Location)")
            else:
                record.location_text = _("(%s Locations)" % record.location_count)

    @api.depends('practitioner_count')
    def _compute_practitioner_text(self):
        for record in self:
            if not record.practitioner_count:
                record.practitioner_text = False
            elif record.practitioner_count == 1:
                record.practitioner_text = _("(1 Practitioner)")
            else:
                record.practitioner_text = _("(%s Practitioners)" % record.practitioner_count)


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
        fields = ["is_pod", "is_company", "is_location", "is_practitioner"]
        # If there's a need to add more fields from parent or other inheriting models, you can do so here.
        return fields

    @api.constrains("is_location", "parent_id")
    def check_location_practice(self):
        test_condition = not config["test_enable"] or self.env.context.get("test_check_location_practice")
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
            (self.is_pod, self._check_pod_user, "pod_base.group_pod_user"),
            (self.is_company, self._check_pod_practice, "pod_base.group_pod_configurator"),
            (self.is_practitioner, self._check_pod_practitioner, "pod_base.group_pod_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_pod_user(self):
        return self.env.user.has_group("pod_base.group_pod_user")
        
    def _check_pod_practice(self):
        return self.env.user.has_group("pod_base.group_pod_configurator")
        
    def _check_pod_practitioner(self):
        return self.env.user.has_group("pod_base.group_pod_configurator")

    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the practitioners of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_pod_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result
