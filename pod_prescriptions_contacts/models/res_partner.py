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
    
    is_partner = fields.Boolean(string='Prescriptions', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_location = fields.Boolean(string='Location', default=False)
    is_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_role_required = fields.Boolean(compute='_compute_is_role_required', inverse='_inverse_is_role_required', string="Is Role Required", store=False)
    is_parent_account = fields.Boolean( string='Parent Practice', related='parent_id.is_company', readonly=True, store=False)
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    practice_type_id = fields.Many2one(string='Practice Type', comodel_name='prescriptions.practice.type')
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
    
    # new_parent_id = fields.Many2one('res.partner', 'Parent', help='select a parent for the child', domain="[('new_parent_id', '=', False), ('type','=','contact')]")
    # new_child_ids = fields.One2many('res.partner', 'new_parent_id', string='Child Customers')
    
    practitioner_role_ids = fields.Many2many(string="Roles", comodel_name="prescriptions.role")
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    patient_ids = fields.One2many("prescriptions.patient", inverse_name="partner_id")
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_counts')
    patient_records = fields.One2many('prescriptions.patient', compute='_compute_patient_records', string="Patients")
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
        elif self.is_company or self.is_location:
            return "base/static/img/company_image.png"
        else:
            return super()._avatar_get_placeholder_path()

    @api.depends('parent_id', 'is_company', 'active')
    def _compute_locations(self):
        for record in self:
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
    def _compute_patient_records(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.patient_records = self.env['prescriptions.patient']  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                record.patient_records = all_partners.mapped('patient_ids')
            else:
                record.patient_records = self.env['prescriptions.patient']

    @api.depends('patient_count')
    def _compute_patient_text(self):
        for record in self:
            if not record.patient_count:
                record.patient_text = False
            elif record.patient_count == 1:
                record.patient_text = _("(1 Patient)")
            else:
                record.patient_text = _("(%s Patients)" % record.patient_count)

    @api.depends('is_practitioner', 'practitioner_role_ids')
    def _compute_is_role_required(self):
        for record in self:
            record.is_role_required = record.is_practitioner and not record.practitioner_role_ids

    def _inverse_is_role_required(self):
        for record in self:
            if record.is_role_required and not record.practitioner_role_ids:
                raise ValidationError("Roles are required for practitioners.")

    @api.constrains('is_practitioner', 'practitioner_role_ids')
    def _check_practitioner_roles(self):
        for record in self:
            if record.is_practitioner and not record.practitioner_role_ids:
                raise ValidationError(_("Roles are required for practitioners."))
    
    @api.model
    def _get_prescriptions_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    # @api.model
    # def fetch_data(self, partner_id):
    #     parent = self.browse(partner_id)
    #     children = parent.new_child_ids
    #     child = []
    #     data_parent = {'parent': {
    #         'name': parent.name,
    #         'image': parent.image_1920},
    #         'child': child}
    #     for rec in children:
    #         data_child = {'name': rec.name,
    #                       'id': rec.id,
    #                       'image': rec.image_1920}
    #         child.append(data_child)
    #     return data_parent

    # def get_formview_action(self, access_uid=None):
    #     print('mmm3',self)
    #     res = super().get_formview_action(access_uid=access_uid)
    #     res.update({
    #         'type': 'ir.actions.act_window',
    #         'name': 'Partner',
    #         'view_mode': 'form',
    #         'res_model': 'res.partner',
    #         'res_id': self.id,
    #     })
    #     return res


    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner in partners:
            if partner.is_partner or partner.patient_ids:
                partner.check_prescription("create")
        return partners

    def write(self, vals):
        result = super().write(vals)
        for partner in self:
            if partner.is_partner or partner.patient_ids:
                partner.check_prescription("write")
        return result

    def unlink(self):
        for partner in self:
            if partner.is_partner or partner.sudo().patient_ids:
                partner.check_prescription("unlink")
        return super().unlink()
    
    def _commercial_sync_to_children(self, visited=None):
        """ Handle sync of commercial fields to descendants """
        if visited is None:
            visited = set()
        # Check if the current partner has already been visited to prevent recursion
        if self.id in visited:
            return

        visited.add(self.id)
        commercial_partner = self.commercial_partner_id
        sync_vals = commercial_partner._update_fields_values(self._commercial_fields())
        sync_children = self.child_ids.filtered(lambda c: not c.is_company)

        # Iterate over child partners and recursively synchronize commercial fields
        for child in sync_children:
            child._commercial_sync_to_children(visited=visited)

        # Update commercial fields for child partners
        res = sync_children.write(sync_vals)
        sync_children._compute_commercial_partner()
        return res

    @api.model
    def default_prescriptions_fields(self):
        fields = ["is_partner", "is_company", "is_location", "is_practitioner"]
        # If there's a need to add more fields from parent or other inheriting models, you can do rx here.
        return fields

    @api.constrains("is_location", "parent_id")
    def check_location_practice(self):
        test_condition = not config["test_enable"] or self.env.context.get("test_check_location_practice")
        if not test_condition:
            return
        for record in self:
            if record.is_location and not record.parent_id:
                raise ValidationError(_("Parent Company must be fullfilled on locations"))

    def check_prescription(self, mode="write"):
        if self.env.su:
            return self._check_prescription(mode=mode)

    def _check_prescription(self, mode="write"):
        if self.sudo().patient_ids:
            self.sudo().patient_ids.check_access_rights(mode)
        
        checks = [
            (self.is_partner, self._check_prescriptions_user, "pod_prescriptions_contacts.group_contacts_user"),
            (self.is_company, self._check_prescriptions_practice, "pod_prescriptions_contacts.group_contacts_configurator"),
            (self.is_practitioner, self._check_prescriptions_practitioner, "pod_prescriptions_contacts.group_contacts_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_prescriptions_user(self):
        return self.env.user.has_group("pod_prescriptions_contacts.group_contacts_user")
        
    def _check_prescriptions_practice(self):
        return self.env.user.has_group("pod_prescriptions_contacts.group_contacts_configurator")
        
    def _check_prescriptions_practitioner(self):
        return self.env.user.has_group("pod_prescriptions_contacts.group_contacts_configurator")

    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the practitioners of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_prescriptions_fields():
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