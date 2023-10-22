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
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_company','=',True)], string="Practice")
    child_ids = fields.One2many("res.partner", compute="_compute_practitioners", string="Practitioners", readonly=True)
    practitioner_role_ids = fields.Many2many(string="Roles", comodel_name="pod.role")
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")
    # internal_code = fields.Char('Internal Code', copy=False)
            
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

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(Partner, self).create(vals_list)
        for partner in partners:
            if partner.is_company:
                partner.ref = self.env['ir.sequence'].next_by_code('pod.practice') or '/'
            elif partner.is_location and partner.parent_id:
                parent_ref = partner.parent_id.ref
                location_number = self.env['res.partner'].search_count([
                    ('parent_id', '=', partner.parent_id.id),
                    ('is_location', '=', True)
                ])
                partner.ref = f"{parent_ref}-{location_number}"
            elif partner.is_practitioner:
                partner.ref = self.env['ir.sequence'].next_by_code('pod.practitioner') or '/'
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("create")
        return partners

    def write(self, vals):
        if 'parent_id' in vals or 'is_location' in vals:
            for partner in self:
                new_parent_id = vals.get('parent_id', partner.parent_id.id)
                new_is_location = vals.get('is_location', partner.is_location)
                if new_is_location and new_parent_id:
                    parent_ref = self.browse(new_parent_id).ref
                    if parent_ref:
                        suffix = 1
                        while self.search([('ref', '=', f"{parent_ref}-{suffix}")]):
                            suffix += 1
                        vals['ref'] = f"{parent_ref}-{suffix}"
        
        result = super(Partner, self).write(vals)
        for partner in self:
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("write")
                
        return result

    @api.model
    def load(self, fields, data):
        ref_index = fields.index('ref')
        is_company_index = fields.index('is_company')
        is_location_index = fields.index('is_location')
        is_practitioner_index = fields.index('is_practitioner')
        parent_id_index = fields.index('parent_id')
        for record in data:
            if record[is_company_index] == '1':
                record[ref_index] = self.env['ir.sequence'].next_by_code('pod.practice') or '/'
            elif record[is_location_index] == '1':
                parent_ref = self.browse(record[parent_id_index]).ref
                location_number = self.env['res.partner'].search_count([
                    ('parent_id', '=', record[parent_id_index]),
                    ('is_location', '=', True)
                ]) + 1
                record[ref_index] = f"{parent_ref}-{location_number}"
            elif record[is_practitioner_index] == '1':
                record[ref_index] = self.env['ir.sequence'].next_by_code('pod.practitioner') or '/'
        return super(Partner, self).load(fields, data)


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
    
 
    def name_get(self):
        res = super(Partner, self).name_get()
        new_res = []
        for record in res:
            partner = self.browse(record[0])
            if partner.is_practitioner:
                name = partner.name
                new_res.append((partner.id, name))
            else:
                new_res.append(record)
        return new_res

