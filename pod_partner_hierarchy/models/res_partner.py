import logging
import json
from lxml import etree
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'incrementing.sequence.mixin']
    _sequence_group = 'parent_id'

    is_company = fields.Boolean(
        string='Account', default=True,
        help="Check this box if this is a Company.")
    is_account = fields.Boolean(
        string='Account', 
        help="Check this box if this is a Customer Account.")
    is_affiliate = fields.Boolean(
        string='Affiliate',
        help="Check this box if this is an Company Affiliate.")
    is_contact = fields.Boolean(
        string='Contact',
        help="Check this box if this is a Company Contact.")
    is_patient = fields.Boolean(
        string='Patient',
        help="Check this box if this is a Patient.")
    
    channel_ids = fields.Many2many(relation='res_partner_channel_rel')
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
  
    commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Mark as True if this partner acts as its own trading company, even with a parent company."
    )

    fax_number = fields.Char(string="Fax")
    customer_code = fields.Char(string="Customer Code", readonly=True, default=lambda self: _("New"))
    legacy_customer_code = fields.Char("Legacy ID", readonly=True)
    parent_relation_label = fields.Char(related='partner_type_id.parent_relation_label', readonly=True)
    parent_id = fields.Many2one('res.partner', index=True, domain=[('is_account','=',True), ('is_company','=',True)], string="Account")
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Account Name')

    parent_type_ids = fields.Many2many(
        'res.partner.type', 
        string='Company types authorized for parent', 
        compute='_compute_parent_types'
    )

    use_parent_address = fields.Boolean(string='Use Parent Address', default=True)

    # Related fields to fetch the parent's address if use_parent_address is True
    parent_street = fields.Char(related='parent_id.street', readonly=True)
    parent_city = fields.Char(related='parent_id.city', readonly=True)
    parent_zip = fields.Char(related='parent_id.zip', readonly=True)
    parent_state_id = fields.Many2one(related='parent_id.state_id', readonly=True)
    parent_country_id = fields.Many2one(related='parent_id.country_id', readonly=True)


    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type', help="Specify the type of partner.")
    partner_type_code = fields.Char(related="partner_type_id.code", store=True, readonly=True)
    partner_company_type = fields.Many2one(
        string="Company Type",
        comodel_name="partner.company.type",
        help="Specify the type of company this belongs to."
    )

    type = fields.Selection([
            ("contact", "Contact Address"),
            ('patient', 'Patient Address'),
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("supplier", "Supplier Address"),
            ("other", "Other Address")],
        string="Address Type",
        store=True,
        default=False,
    )


    company_address_type = fields.Selection(
        selection=[
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("supplier", "Supplier Address"),
            ("other", "Other Address"),
        ],
        string="Company Address Type",
        compute="_compute_company_address_type",
        inverse="_inverse_company_address_type",
        store=True,  # ✅ Ensure the computed value is stored in the database
        required=True,  # ✅ Forces selection
    )

    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_affiliate", "=", True)],
    )

    # org_chart_affiliate_ids = fields.One2many(
    #     related="affiliate_ids",
    #     string="Direct Affiliates",
    # )

    affiliates_count = fields.Integer('Number of Affiliates', compute='_compute_affiliates_count', compute_sudo=True)
    companies_label = fields.Char(related='partner_type_id.companies_label', readonly=True)

    child_ids = fields.One2many(domain=[("active", "=", True), ("is_company", "=", False), ("is_contact", "=", True)])

    # org_chart_contact_ids = fields.One2many(
    #     related="child_ids",
    #     string="Direct Contacts",
    # )

    sub_contact_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Contacts",
        compute="_compute_sub_contact_ids",
        # store=False,
        help="Indirectly associated contacts (grandchildren)."
    )

    contacts_count = fields.Integer('Number of Contacts', compute='_compute_contacts_count')
    responsible_contact_id = fields.Many2one(
        'res.partner',
        string="Responsible Contact",
        domain="[('parent_id', '=', parent_id), ('is_company', '=', False)]",
    )

    # Patient and Sub-Patient Fields
    patient = fields.Boolean(string="Is a Patient", compute="_compute_patient_ids", store=True)
        # Sub Affiliates
    sub_affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Affiliates",
        compute="_compute_sub_affiliate_ids",
        # store=False,
        help="Indirectly associated affiliates (grandchildren)."
    )


    patient_ids = fields.One2many('res.partner', 'parent_id', domain=[('is_patient', '=', True)])
    patients_count = fields.Integer('Number of Patients', compute='_compute_patients_count')
    sub_patient_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Patients",
        compute="_compute_sub_patient_ids",
    )

    # Prescriptions
    patient_prescriptions = fields.One2many(
        'orthotic.prescription', 'partner_id', string="Prescriptions"
    )


    # Sale Orders
    sale_order_ids = fields.One2many("sale.order", "partner_id", string="Sale Orders")
    current_sale_order_ids = fields.One2many(
        "sale.order", compute="_compute_current_sale_order_ids", string="Current Orders"
    )
    historic_sale_order_ids = fields.One2many(
        "sale.order", compute="_compute_historic_sale_order_ids", string="Historic Orders"
    )
    reorder_count = fields.Integer(compute="_compute_reorder_order_count", string="Reorder")

    # Compute and Inverse Methods
    @api.depends("type")
    def _compute_company_address_type(self):
        for record in self:
            if not record.company_address_type:  # ✅ Only set if empty
                if record.type in dict(self._fields["company_address_type"].selection):
                    record.company_address_type = record.type
                else:
                    record.company_address_type = False  # ✅ Keep it empty if not set


    def _inverse_company_address_type(self):
        for record in self:
            if record.company_address_type:
                record.type = record.company_address_type

    @api.depends('partner_type_id')
    def _compute_parent_types(self):
        for partner in self:
            if partner.partner_type_id:
                partner.parent_type_ids = partner.partner_type_id.parent_type_ids
            else:
                partner.parent_type_ids = self.env['res.partner.type'].browse()

    @api.depends('partner_type_id')
    def _compute_partner_type_infos(self):
        for partner in self:
            partner.can_have_parent = partner.partner_type_id.can_have_parent
            partner.parent_is_required = partner.partner_type_id.parent_is_required

    @api.model
    def default_get(self, fields):
        _logger.debug("Context Passed to default_get: %s", self._context)
        res = super(Partner, self).default_get(fields)

        # Remove automatic parent assignment logic
        if res.get("is_affiliate") and not res.get("parent_id"):
            res["parent_id"] = False  # Explicitly ensure the field is empty
            _logger.info("Parent ID left empty for manual selection.")

        return res


    # Affiliates
    @api.depends('affiliate_ids')
    def _compute_affiliates_count(self):
        for partner in self:
            partner.affiliates_count = len(partner.affiliate_ids)

    def _get_all_sub_affiliates(self):
        """
        Recursively fetch all sub-affiliates for the current partner, excluding direct affiliates.
        """
        sub_affiliates = self.env["res.partner"]
        for affiliate in self.affiliate_ids:
            sub_affiliates |= affiliate.affiliate_ids  # Direct affiliates of the current affiliate
            sub_affiliates |= affiliate._get_all_sub_affiliates()  # Recursively fetch deeper levels
        return sub_affiliates

    @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
    def _compute_sub_affiliate_ids(self):
        """
        Compute sub-affiliates for each partner.
        """
        for partner in self:
            all_sub_affiliates = partner._get_all_sub_affiliates()
            partner.sub_affiliate_ids = all_sub_affiliates - partner.affiliate_ids  # Exclude direct affiliates

    # Contacts
    @api.depends('child_ids')
    def _compute_contacts_count(self):
        for partner in self:
            partner.contacts_count = len(partner.child_ids)

    def _get_all_sub_contacts(self):
        """
        Recursively fetch all sub-contacts for the current company,
        excluding direct child contacts and patients.
        """
        sub_contacts = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if not child.is_company and not child.is_patient:  # Exclude patients and include only non-companies
                    _logger.debug("Adding direct child contact: %s (ID: %s)", child.name, child.id)
                    sub_contacts |= child  # Include the direct child contact
                # Recursively fetch all contacts for the child, including deeper levels
                sub_contacts |= child._get_all_sub_contacts()
        return sub_contacts
    
    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_contact_ids(self):
        """
        Compute sub-contacts for the current company, excluding patients.
        """
        for partner in self:
            if partner.is_company:  # Ensure we compute for companies only
                _logger.debug("Computing sub-contacts for company: %s (ID: %s)", partner.name, partner.id)
                all_sub_contacts = partner._get_all_sub_contacts()
                # Exclude direct child contacts from the results
                final_sub_contacts = all_sub_contacts - partner.child_ids.filtered(
                    lambda c: not c.is_company and not c.is_patient
                )
                _logger.debug("Final sub-contacts for company %s (ID: %s): %s", partner.name, partner.id, final_sub_contacts)
                partner.sub_contact_ids = final_sub_contacts
            else:
                partner.sub_contact_ids = self.env["res.partner"]  # Empty for non-companies

    # Patients
    @api.depends('patient_ids')
    def _compute_patient_ids(self):
        for partner in self:
            partner.patient = partner.child_ids.filtered(lambda c: c.is_patient)

    @api.depends('patient_ids')
    def _compute_patients_count(self):
        for partner in self:
            partner.patients_count = len(partner.patient_ids)

    def _get_all_sub_patients(self):
        """
        Recursively fetch all sub-patients for the current company,
        excluding direct child patients.
        """
        sub_patients = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if child.is_patient:  # Include only patients
                    _logger.debug("Adding direct child patient: %s (ID: %s)", child.name, child.id)
                    sub_patients |= child  # Include the direct child patient
                # Recursively fetch all sub-patients for the child, including deeper levels
                sub_patients |= child._get_all_sub_patients()
        return sub_patients
    
    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_patient_ids(self):
        """
        Compute sub-patients for the current company.
        """
        for partner in self:
            if partner.is_company:  # Ensure we compute for companies only
                _logger.debug("Computing sub-patients for company: %s (ID: %s)", partner.name, partner.id)
                all_sub_patients = partner._get_all_sub_patients()
                # Exclude direct child patients from the results
                partner.sub_patient_ids = all_sub_patients - partner.patient_ids
                _logger.debug("Final sub-patients for company %s (ID: %s): %s", partner.name, partner.id, partner.sub_patient_ids)
            else:
                partner.sub_patient_ids = self.env["res.partner"]  # Empty for non-companies

    # Sales Orders
    @api.depends("sale_order_ids")
    def _compute_current_sale_order_ids(self):
        for partner in self:
            partner.current_sale_order_ids = partner.sale_order_ids.filtered(lambda o: o.state not in ("done", "cancel"))

    @api.depends("sale_order_ids")
    def _compute_historic_sale_order_ids(self):
        for partner in self:
            partner.historic_sale_order_ids = partner.sale_order_ids.filtered(lambda o: o.state in ("done", "cancel"))

    @api.depends("sale_order_ids")
    def _compute_reorder_order_count(self):
        for partner in self:
            partner.reorder_count = len(partner.historic_sale_order_ids)

    # Constraints
    @api.constrains('parent_id', 'partner_type_code', 'is_affiliate')
    def _check_no_circular_reference(self):
        for partner in self:
            # Existing circular reference check
            if partner.parent_id and partner.parent_id.id == partner.id:
                raise ValidationError(_("A partner cannot be its own parent."))

            visited = set()
            current = partner.parent_id
            while current:
                if current.id in visited:
                    raise ValidationError(_("Circular reference detected in the hierarchy."))
                visited.add(current.id)
                current = current.parent_id

            # Additional check for affiliates
            if partner.is_patient and not partner.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))


    @api.constrains('parent_id', 'is_affiliate')
    def _check_affiliate_parent_constraint(self):
        for record in self:
            if record.is_affiliate and not record.parent_id:
                if record.create_date:  # Ensure the record has been saved
                    raise ValidationError(_("Affiliates must have a parent account."))


    # Onchange Methods
    # @api.onchange('use_parent_address')
    # def _onchange_use_parent_address(self):
    #     if self.use_parent_address and self.parent_id:
    #         self.street = self.parent_id.street
    #         self.city = self.parent_id.city
    #         self.zip = self.parent_id.zip
    #         self.state_id = self.parent_id.state_id
    #         self.country_id = self.parent_id.country_id
    #     elif not self.use_parent_address:
    #         self.street = False
    #         self.city = False
    #         self.zip = False
    #         self.state_id = False
    #         self.country_id = False

    @api.onchange('use_parent_address', 'parent_id')
    def _onchange_use_parent_address(self):
        if self.use_parent_address and self.parent_id:
            self.street = self.parent_id.street
            self.street2 = self.parent_id.street2
            self.city = self.parent_id.city
            self.zip = self.parent_id.zip
            self.state_id = self.parent_id.state_id
            self.country_id = self.parent_id.country_id
        elif not self.use_parent_address:
            self.street = ''
            self.street2 = ''
            self.city = ''
            self.zip = ''
            self.state_id = False
            self.country_id = False



    @api.onchange('company_type')
    def _onchange_company_type(self):
        """Update partner_type_id based on the selected company_type using boolean fields."""
        if self.company_type == 'company':
            partner_type_field = 'is_account' if self.is_account else 'is_affiliate'
        elif self.company_type == 'person':
            partner_type_field = 'is_patient' if self.is_patient else 'is_contact'
        else:
            partner_type_field = 'is_contact'  # Default fallback

        # Search for the matching partner type dynamically
        self.partner_type_id = self.env['res.partner.type'].search(
            [(partner_type_field, '=', True)], limit=1
        )


    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        self.apply_contact_logic()
        domain = [("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))
        return {"domain": {"responsible_contact_id": domain}}

    @api.onchange("partner_type_id")
    def _onchange_partner_type(self):
        if self.partner_type_id:
            self.update(self._get_inherit_values(self.partner_type_id))
            if self.partner_type_id.type == 'contact':
                self.is_contact = True
                self.type = False
            else:
                self.is_contact = False
                self.type = self.partner_type_id.type if self.partner_type_id.type in dict(self._fields['type'].selection).keys() else False



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

    def apply_contact_logic(self):
        if self.parent_id:
            contacts = self.env["res.partner"].search([
                ("parent_id", "=", self.parent_id.id),
                ("is_company", "=", False)
            ])
            if contacts:
                self.responsible_contact_id = contacts[0]

    # Validation helper method
    def _validate_affiliate_parent(self):
        for record in self:
            if not record.id:  # Skip validation for new (unsaved) records
                continue
            if record.is_affiliate and not record.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))


    @api.model
    def create(self, vals):
        _logger.debug("Received vals for create: %s", vals)

        if vals.get("parent_id"):
            vals["parent_id"] = int(vals["parent_id"])

        if vals.get("customer_code", _("New")) == _("New"):
            vals["customer_code"] = self._generate_reference(vals)
            _logger.debug("Generated customer_code: %s", vals["customer_code"])

        return super(Partner, self).create(vals)


    def write(self, vals):
        _logger.info("Updating partner(s) with values: %s", vals)

        needs_code_update = any(
            key in vals for key in ["parent_id", "is_account", "is_affiliate", "is_contact", "is_patient"]
        )

        for partner in self:
            if (needs_code_update or partner.customer_code == _("New")):
                _logger.info("Regenerating customer_code for partner ID: %s", partner.id)
                vals["customer_code"] = self._generate_reference(vals)
                _logger.info("Updated customer_code: %s", vals["customer_code"])

        result = super(Partner, self).write(vals)
        self._validate_affiliate_parent()
        self._update_children(vals)
        _logger.info("Partner(s) updated successfully.")

        return result


    # def _generate_reference(self, vals):
    #     _logger.debug("Generating reference with vals: %s", vals)

    #     if isinstance(vals, str):
    #         return vals

    #     if not isinstance(vals, dict):
    #         raise ValidationError(_("Invalid data passed for reference generation."))

    #     sequence_map = {
    #         "is_account": "res.partner.account",
    #         "is_affiliate": "res.partner.affiliate",
    #         "is_contact": "res.partner.contact",
    #         "is_patient": "res.partner.patient"
    #     }

    #     for key, seq_code in sequence_map.items():
    #         if vals.get(key):
    #             new_code = self.env["ir.sequence"].next_by_code(seq_code)
    #             if not new_code:
    #                 raise ValidationError(_("Unable to generate sequence for %s" % key))
    #             return new_code

    #     new_code = self.env["ir.sequence"].next_by_code("res.partner.generic")
    #     if not new_code:
    #         raise ValidationError(_("Unable to generate generic customer code."))
    #     return new_code


    def _generate_reference(self, vals):
        _logger.debug("Generating reference with vals: %s", vals)

        if isinstance(vals, str):
            return vals

        if not isinstance(vals, dict):
            raise ValidationError(_("Invalid data passed for reference generation."))

        sequence_map = {
            "is_account": "res.partner.account",
            "is_affiliate": "res.partner.affiliate",
            "is_contact": "res.partner.contact",
            "is_patient": "res.partner.patient"
        }

        new_code = ""
        for key, seq_code in sequence_map.items():
            if vals.get(key):
                generated_code = self.env["ir.sequence"].next_by_code(seq_code)
                if not generated_code:
                    raise ValidationError(_("Unable to generate sequence for %s" % key))
                
                # Check if it's an affiliate and has a parent
                parent_id = vals.get("parent_id")
                if vals.get("is_affiliate") and parent_id:
                    parent = self.env["res.partner"].browse(parent_id)
                    if parent.exists() and parent.customer_code:
                        new_code = f"{parent.customer_code}{generated_code}"
                    else:
                        new_code = generated_code  # Fallback if parent doesn't exist or has no code
                else:
                    new_code = generated_code

                return new_code

        # Fallback for generic sequence
        new_code = self.env["ir.sequence"].next_by_code("res.partner.generic")
        if not new_code:
            raise ValidationError(_("Unable to generate generic customer code."))
        return new_code


    def view_affiliates(self):
        return {
            'name': _('Affiliates'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'tree,form',
            'view_id': False,
            'domain': [
                ('parent_id', 'in', self.ids),
                ('is_affiliate', '=', True)
            ],
            'target': 'current',
        } 
    
    def _update_fields_view_get_result(self, result, view_type='form'):
        if view_type == 'form' and not self._context.get('display_original_view'):
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field[@name='child_ids']"):
                node.set('modifiers', json.dumps({
                    'default_is_account': False,
                    'default_is_affiliate': False,
                    'default_is_contact': False,
                    'default_is_patient': False,
                }))
            result['arch'] = etree.tostring(doc)
        return result

    def get_view(self, view_id=None, view_type='form', **options):
        result = super(Partner, self).get_view(view_id, view_type, **options)
        node = etree.fromstring(result['arch'])
        view_fields = set(el.get('name') for el in node.xpath('.//field[not(ancestor::field)]'))
        result['fields'] = self.fields_get(view_fields)
        return self._update_fields_view_get_result(result, view_type)

    @api.model
    def _format_args(self, args):
        for cond in (args or []):
            if len(cond) == 3 and cond[2] and isinstance(cond[2], list) and \
                isinstance(cond[2][0], list):
                for index, item in enumerate(cond[2]):
                    if item[0] == 1:
                        cond[2][index] = item[1]
                    elif item[0] == 6:
                        cond[2] = item[2]
                        break

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        self._format_args(args)
        return super(Partner, self).name_search(name, args, operator, limit)

    def _search(self, args, offset=0, limit=None, order=None, count=False):
        self._format_args(args)
        if count:
            return super(Partner, self)._search(args, offset=offset, limit=limit, order=order, count=True)
        return super(Partner, self)._search(args, offset=offset, limit=limit, order=order)

