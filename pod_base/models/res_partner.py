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
    
    def name_get(self):
        res = []
        for record in self:
            name = record.name or ''
            if record.is_company:
                res.append((record.id, name))
            else:
                res.append((record.id, name if not record.parent_id else record.parent_id.name))
                return res
    
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
    

    # def action_view_practice_flags(self):
    #     return self._get_action_partner_view_flags("practice_flag_ids", "default_practice_id")

    # def action_view_practitioner_flags(self):
    #     return self._get_action_partner_view_flags("practitioner_flag_ids", "default_practitioner_id")
        
              

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
