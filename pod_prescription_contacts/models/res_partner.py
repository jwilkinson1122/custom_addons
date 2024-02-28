import logging
import base64
import json

from dateutil.relativedelta import relativedelta

from odoo import _, models, fields, tools, api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "res.partner"
    
    is_partner = fields.Boolean(string='Prescription', default=False)
    is_parent_account = fields.Boolean(string='Location', default=False)
    is_company = fields.Boolean(string='Company', default=False)
    is_location = fields.Boolean(string='Location', default=False)
    is_practitioner = fields.Boolean(string='Practitioner', default=False)
    is_role_required = fields.Boolean(compute='_compute_is_role_required', inverse='_inverse_is_role_required', string="Is Role Required", store=False)
    # is_parent_account = fields.Boolean( string='Parent Account', related='parent_id.is_company', readonly=True, store=False)
    
    ref = fields.Char(string="Customer Number", index=True)
    # ref = fields.Char("Customer Number", readonly=True, default=lambda self: _("New"))
    # internal_code = fields.Char('Internal Code', copy=False)
    internal_code = fields.Char("Internal Code", readonly=True, default=lambda self: _("New"))
    
    # account_code = fields.Char('Account code')
    # _sql_constraints = [
    #     ('account_coder_unique', 
    #     'unique(account_code)',
    #     'Choose another value of account code - it has to be unique!')
    # ]

    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_parent_account','=',True), ('is_company','=',True)], string="Account", groups="base.group_no_one")
    
    # parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')

    
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    location_count = fields.Integer(string='Location Count', compute='_compute_location_and_practitioner_counts')
    location_text = fields.Char(compute="_compute_location_text")
    practice_type_id = fields.Many2one(string='Practice Type', comodel_name='prescription.practice.type')
    practice_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Practice Type', default='clinic')
    fax_number = fields.Char(string="Fax")
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Attached To:', readonly=True)
    child_ids = fields.One2many("res.partner", compute="_compute_practitioners", string="Practitioners", readonly=True)
    practitioner_role_ids = fields.Many2many(string="Roles", comodel_name="prescription.role")
    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_location_and_practitioner_counts')
    practitioner_text = fields.Char(compute="_compute_practitioner_text")
    patient_ids = fields.One2many("prescription.patient", inverse_name="partner_id")
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_counts')
    patient_records = fields.One2many('prescription.patient', compute='_compute_patient_records', string="Patients")
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
        elif self.is_parent_account or self.is_company or self.is_location:
            return "base/static/img/company_image.png"
        else:
            return super()._avatar_get_placeholder_path()
        

    def find_res_partner_by_ref_using_barcode(self, barcode):
        partner = self.search([("ref", "=", barcode)], limit=1)
        if not partner:
            xmlid = "barcode_action.res_partner_find"
            action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
            context = safe_eval(action["context"])
            context.update(
                {
                    "default_state": "warning",
                    "default_status": _(
                        "Partner with Internal Reference " "%s cannot be found"
                    )
                    % barcode,
                }
            )
            action["context"] = json.dumps(context)
            return action
        xmlid = "base.action_partner_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        res = self.env.ref("base.view_partner_form", False)
        action["views"] = [(res and res.id or False, "form")]
        action["res_id"] = partner.id
        return action

        

    root_ancestor = fields.Many2one(comodel_name='res.partner',
                                    string='Root Ancestor',
                                    compute='_compute_root_ancestor',
                                    store=True,
                                    recursive=True)

    @api.depends('parent_id', 'parent_id.root_ancestor')
    def _compute_root_ancestor(self):
        for rec in self:
            rec.root_ancestor = rec.parent_id and rec.parent_id.root_ancestor or rec

    child_count = fields.Integer(compute='_compute_child_count', string='# of Child')

    def _compute_child_count(self):
        for partner in self:
            partner.child_count = len(partner.child_ids)
    
    @api.depends('parent_id', 'is_parent_account', 'is_company', 'is_location', 'active')
    def _compute_locations(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_locations = self.env['res.partner'].search([
                    ('id', 'child_of', record.id),
                    ("is_parent_account", "=", False),  
                    ("is_company", "=", True), 
                    ("is_location", "=", True), 
                    ("patient_ids", "=", False),  
                    ("active", "=", True)
                ])
                record.location_ids = all_locations - record
            else:
                record.location_ids = self.env['res.partner'] 

    # @api.depends('parent_id', 'is_company', 'is_location', 'is_practitioner', 'active')
    # def _compute_locations(self):
    #     for record in self:
    #         if not isinstance(record.id, models.NewId):
    #             all_locations = self.env['res.partner'].search([
    #                 ('id', 'child_of', record.id), 
    #                 ("is_company", "=", False),
    #                 ("is_location", "=", True),
    #                 ("is_practitioner", "=", False),  
    #                 ("patient_ids", "=", False),  
    #                 ("active", "=", True)
    #             ])
    #             record.location_ids = all_locations - record
    #         else:
    #             record.location_ids = self.env['res.partner']
  
    @api.depends('location_count')
    def _compute_location_text(self):
        for record in self:
            if not record.location_count:
                record.location_text = False
            elif record.location_count == 1:
                record.location_text = _("(1 Location)")
            else:
                record.location_text = _("(%s Locations)" % record.location_count)


    # @api.depends('child_ids', 'child_ids.is_company')
    # def _compute_practitioners(self):
    #     for record in self:
    #         if not isinstance(record.id, models.NewId):
    #             all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
    #             all_partners -= record

    #             practitioners = all_partners.filtered(lambda p: not p.is_company and not p.patient_ids)
    #             record.child_ids = practitioners
    #         else:
    #             record.child_ids = self.env['res.partner']

    @api.depends('parent_id', 'is_company', 'is_practitioner', 'active')
    def _compute_practitioners(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_practitioners = self.env['res.partner'].search([
                    ('id', 'child_of', record.id),
                    # ("is_parent_account", "=", False), 
                    ("is_company", "=", False),
                    # ("is_location", "=", False),
                    ("is_practitioner", "=", True),  
                    ("patient_ids", "=", False),  
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
    def _compute_patient_records(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.patient_records = self.env['prescription.patient']  # Assigning a default value for new records
                continue

            if record.is_practitioner or record.is_company:
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record
                record.patient_records = all_partners.mapped('patient_ids')
            else:
                record.patient_records = self.env['prescription.patient']

    # def action_show_patients(self):
    #         self.ensure_one()
    #         action = {
    #             'name': _('Patients'),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'prescription.patient',  
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
    
    @api.model
    def _get_prescription_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

 
    # @api.model
    # def create(self, vals):
    #     if vals.get("internal_code", _("New")) == _("New"):
    #         vals["internal_code"] = self.env["ir.sequence"].next_by_code("partner.internal.code") or _("New")
    #     return super(Partner, self).create(vals)
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     partners = super().create(vals_list)
    #     for partner in partners:
    #         if partner.is_partner or partner.patient_ids:
    #             partner.check_prescription("create")
    #         if not partner.internal_code and partner.parent_id:
    #             parent_partner = partner.parent_id
    #             if parent_partner.internal_code:
    #                 internal_code = parent_partner.internal_code + '1' 
    #                 partner.write({'internal_code': internal_code})
    #         elif not partner.internal_code:
    #             partner.write({'internal_code': self.env['ir.sequence'].next_by_code('partner.internal.code')})

    #     return partners
    

    @api.model
    def create(self, vals):
        # If internal_code is not provided or set to "New", generate a new code
        if not vals.get("internal_code") or vals.get("internal_code") == _("New"):
            vals["internal_code"] = self.env["ir.sequence"].next_by_code("partner.internal.code") or _("New")
        # Call the original create method to create the partner
        partner = super().create(vals)
        
        # Check if the partner is a partner or has patient_ids
        if partner.is_partner or partner.patient_ids:
            partner.check_prescription("create")

        # If internal code is not provided, generate it based on the parent's internal code
        if not partner.internal_code and partner.parent_id:
            parent_partner = partner.parent_id
            if parent_partner.internal_code:
                # Append a digit to the parent's internal code
                internal_code = parent_partner.internal_code + '1'  # Modify this as needed
                partner.write({'internal_code': internal_code})
        elif not partner.internal_code:
            # If no parent, generate a new internal code
            partner.write({'internal_code': self.env['ir.sequence'].next_by_code('partner.internal.code')})

        return partner

    

    # _sql_constraints = {('internal_code_uniq', 'unique(internal_code)', 'Internal Code must be unique!')}


    def write(self, vals):
        result = super().write(vals)
        for partner in self:
            if partner.is_partner or partner.patient_ids:
                partner.check_prescription("write")
        return result

    # def write(self, vals):
    #     partners_by_type = {}
    #     if vals.get('partner_type_id'):
    #         partner_type = self.env['res.partner.type'].browse(
    #             vals['partner_type_id'])
    #         partners_by_type[partner_type] = self
    #     else:
    #         for partner in self:
    #             partners_by_type.setdefault(
    #                 partner.partner_type_id, self.browse())
    #             partners_by_type[partner.partner_type_id] |= partner
    #     for partner_type in partners_by_type:
    #         if list(vals.keys()) != ['is_company']:  # To avoid infinite loop
    #             vals.update(self._get_inherit_values(
    #                 partner_type, not_null=True))
    #         super(Partner, partners_by_type[partner_type]).write(vals)
    #     self._update_children(vals)
    #     return True

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
        for child in sync_children: child._commercial_sync_to_children(visited=visited)

        # Update commercial fields for child partners
        res = sync_children.write(sync_vals)
        sync_children._compute_commercial_partner()
        return res

    
    @api.model
    def default_prescription_fields(self):
        fields = ["is_partner", "is_parent_company", "is_company", "is_location", "is_practitioner"]
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
            (self.is_partner, self._check_prescription_user, "pod_prescription_contacts.group_contacts_user"),
            (self.is_company, self._check_prescription_practice, "pod_prescription_contacts.group_contacts_configurator"),
            (self.is_practitioner, self._check_prescription_practitioner, "pod_prescription_contacts.group_contacts_configurator")
        ]
        
        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info("Access Denied by ACLs for operation: %s, uid: %s, model: %s", mode, self._uid, self._name)
                raise AccessError(_("You are not allowed to %(mode)s Contacts (res.partner) records.", mode=mode))

    def _check_prescription_user(self):
        return self.env.user.has_group("pod_prescription_contacts.group_contacts_user")
        
    def _check_prescription_practice(self):
        return self.env.user.has_group("pod_prescription_contacts.group_contacts_configurator")
        
    def _check_prescription_practitioner(self):
        return self.env.user.has_group("pod_prescription_contacts.group_contacts_configurator")

    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the practitioners of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_prescription_fields():
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


    def _get_name(self):
        """Utility method to allow name_get to be overrided without re-browse the partner"""
        partner = self
        name = partner.name or ""

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ["invoice", "delivery", "other"]:
                name = dict(self.fields_get(["type"])["type"]["selection"])[
                    partner.type
                ]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get("show_address_only"):
            name = partner._display_address(without_company=True)
        if self._context.get("show_address"):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace("\n\n", "\n")
        name = name.replace("\n\n", "\n")
        if self._context.get("address_inline"):
            splitted_names = name.split("\n")
            name = ", ".join([n for n in splitted_names if n.strip()])
        if self._context.get("show_email") and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get("html_format"):
            name = name.replace("\n", "<br/>")
        if self._context.get("show_vat") and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)

        if (
            not self._context.get("show_address_only")
            and not self._context.get("show_address")
            and not self._context.get("address_inline")
        ):
            name = "%s ‒ %s" % (name, partner.id)
        return name


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