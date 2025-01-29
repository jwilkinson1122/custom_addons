import logging
import json
from lxml import etree
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# _inherit = ['mrp.workcenter', 'mail.thread', 'mail.activity.mixin',]
# _inherit = ['mrp.workcenter', 'mail.thread', 'mail.activity.mixin']

# class RecurrenceRule(models.Model):
#     _name = 'calendar.recurrence'
#     _inherit = ['calendar.recurrence', 'microsoft.calendar.sync']



class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'incrementing.sequence.mixin']
    _sequence_group = 'parent_id'

    is_account = fields.Boolean(
        string='Account', default=True,
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
    
    # channel_ids = fields.Many2many(relation='mail_channel_library_book_partner')
    # channel_ids = fields.Many2many(
    #     'res.partner.type',
    #     'res_partner_channel_rel',
    #     'partner_id',
    #     'channel_id',
    #     string="Partner Channels"
    # )

    channel_ids = fields.Many2many(relation='res_partner_channel_rel')

    
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
  
    commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Mark as True if this partner acts as its own trading company, even with a parent company."
    )
    # Field Declarations
    fax_number = fields.Char(string="Fax")
    customer_code = fields.Char(string="Customer Code", readonly=True, default=lambda self: _("New"))
    legacy_customer_code = fields.Char("Legacy ID", readonly=True)
    parent_relation_label = fields.Char(related='partner_type_id.parent_relation_label', readonly=True)
    
    # Computed Fields
    parent_id = fields.Many2one(ondelete='restrict')
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')

    parent_type_ids = fields.Many2many(
        'res.partner.type', 
        string='Company types authorized for parent', 
        compute='_compute_parent_types'
    )

    partner_type_code = fields.Char(related="partner_type_id.code", store=True, readonly=True)

    type = fields.Selection(
        selection_add=[
            ("contact", "Contact Address"),
            ("patient", "Patient Address"),
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("supplier", "Supplier Address"),
            ("other", "Other Address"),
        ],
        string="Address Type",
        default=False,
    )

    partner_company_type = fields.Many2one(
        string="Company Type",
        comodel_name="partner.company.type",
        help="Specify the type of company this belongs to."
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
        store=True,
    )

    contact_address_type = fields.Selection(
        selection=[
            ("contact", "Contact Address"),
            ("patient", "Patient Address"),
        ],
        string="Contact Address Type",
        compute="_compute_contact_address_type",
        inverse="_inverse_contact_address_type",
        store=True,
    )

    # Affiliate Fields
    # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_affiliate", "=", True)],
    )

    # child_ids = fields.One2many('res.partner', 'parent_id', string='Contact', domain=[('active', '=', True)])


    affiliates_count = fields.Integer('Number of Affiliates', compute='_compute_affiliates_count', compute_sudo=True)
    companies_label = fields.Char(related='partner_type_id.companies_label', readonly=True)

    
    # Contact Fields
    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(domain=[("active", "=", True), ("is_company", "=", False), ("is_contact", "=", True)])

    # Sub Contacts
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


    @api.depends('partner_type_id')
    def _compute_parent_types(self):
        for partner in self:
            if partner.partner_type_id:
                partner.parent_type_ids = partner.partner_type_id.parent_type_ids
            else:
                partner.parent_type_ids = self.env['res.partner.type'].browse()

    # @api.depends('partner_type_id')
    # def _compute_partner_type_infos(self):
    #     """Compute parent-related fields based on partner type."""
    #     for partner in self:
    #         partner.can_have_parent = True
    #         partner.parent_is_required = False
    #         if partner.partner_type_id and partner.partner_type_id.can_have_parent:
    #             partner.can_have_parent = True
    #             partner.parent_is_required = partner.partner_type_id.parent_is_required

    @api.depends('partner_type_id')
    def _compute_partner_type_infos(self):
        for partner in self:
            partner.can_have_parent = partner.partner_type_id.can_have_parent
            partner.parent_is_required = partner.partner_type_id.parent_is_required


    @api.depends("type")
    def _compute_company_address_type(self):
        for record in self:
            record.company_address_type = record.type if record.type in dict(self._fields["company_address_type"].selection) else False

    @api.model
    def default_get(self, fields):
        _logger.debug("Context Passed to default_get: %s", self._context)
        res = super(Partner, self).default_get(fields)

        partner_type_code = self._context.get('default_partner_type_code', 'CONTACT')  # Default to CONTACT
        partner_type = self.env['res.partner.type'].search([('code', '=', partner_type_code)], limit=1)
        
        if partner_type:
            res['partner_type_id'] = partner_type.id

        res.setdefault('company_type', 'person' if partner_type_code == 'PATIENT' else 'company')
        
        return res



    @api.depends("type")
    def _compute_contact_address_type(self):
        for record in self:
            record.contact_address_type = record.type if record.type in dict(self._fields["contact_address_type"].selection) else False

    def _inverse_company_address_type(self):
        for record in self:
            record.type = record.company_address_type if record.company_address_type else record.type

    def _inverse_contact_address_type(self):
        for record in self:
            record.type = record.contact_address_type if record.contact_address_type else record.type

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
    # @api.constrains('parent_id')
    # def _check_no_circular_reference(self):
    #     for partner in self:
    #         if partner.parent_id and partner.parent_id.id == partner.id:
    #             raise ValidationError(_("A partner cannot be its own parent."))

    #         visited = set()
    #         current = partner.parent_id
    #         while current:
    #             if current.id in visited:
    #                 raise ValidationError(_("Circular reference detected in the hierarchy."))
    #             visited.add(current.id)
    #             current = current.parent_id

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
            if partner.partner_type_code == "AFFILIATE" and not partner.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))

    @api.constrains('parent_id', 'partner_type_code', 'is_affiliate')
    def _check_affiliate_parent_constraint(self):
        for record in self:
            if record.partner_type_code == "AFFILIATE" and not record.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))

    # Onchange Methods
    @api.onchange('company_type')
    def _onchange_company_type(self):
        type_mapping = {
            'company': 'ACCOUNT' if self.is_account else 'AFFILIATE',
            'person': 'PATIENT' if self.is_patient else 'CONTACT',
        }
        code = type_mapping.get(self.company_type, 'CONTACT')
        self.partner_type_id = self.env['res.partner.type'].search([('code', '=', code)], limit=1)


    # @api.onchange("parent_id")
    # def _onchange_parent_id(self):
    #     self.apply_contact_logic()
    #     domain = [("is_company", "=", False)]
    #     if self.parent_id:
    #         domain.append(("parent_id", "=", self.parent_id.id))
    #     return {"domain": {"responsible_contact_id": domain}}

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        self.apply_contact_logic()

        # Enforce validation for affiliates
        if self.partner_type_code == "AFFILIATE" and not self.parent_id:
            raise ValidationError(_("Affiliates must have a parent account."))

        domain = [("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))
        return {"domain": {"responsible_contact_id": domain}}

     
    @api.onchange('partner_type_id')
    def _onchange_partner_type(self):
        """Handle changes in partner type to update parent-related fields."""
        self.update(self._get_inherit_values(self.partner_type_id))

        # Skip validation if no parent is set yet (e.g., during default initialization)
        if not self.parent_id and self._context.get('default_partner_type_code') == 'AFFILIATE':
            return

        # Enforce validation for affiliates
        if self.partner_type_code == "AFFILIATE" and not self.parent_id:
            raise ValidationError(_("Affiliates must have a parent account."))

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
            # Skip validation during default initialization
            if self._context.get('default_partner_type_code') == 'AFFILIATE' and not record.parent_id:
                continue

            # Enforce validation for finalized affiliates
            if record.partner_type_code == "AFFILIATE" and not record.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))
            

    @api.model
    def create(self, vals):
        """
        Handles partner creation with validation, customer code generation,
        and partner type inheritance logic. Allows creation of Affiliates 
        only when a valid parent is provided.
        """
        _logger.debug("Received vals for create: %s", vals)

        # Ensure parent_id is an integer
        if vals.get("parent_id"):
            vals["parent_id"] = int(vals["parent_id"])
        
        # Check Affiliate validation
        if vals.get("is_affiliate"):
            parent_id = vals.get("parent_id")
            _logger.debug("Checking parent_id: %s", parent_id)

            if not parent_id:
                _logger.error("Affiliates must have a parent account. Parent ID is missing!")
                raise ValidationError(_("Affiliates must have a parent account."))

            # Fetch parent using search instead of browse
            parent_partner = self.env["res.partner"].search([("id", "=", parent_id)], limit=1)
            _logger.debug("Parent Partner Fetched: %s", parent_partner)
            _logger.debug("Parent Partner Exists: %s", parent_partner.exists())
            _logger.debug("Parent Partner is_account: %s", parent_partner.is_account)

            if not parent_partner.exists():
                _logger.error("The specified parent account does not exist. ID: %s", parent_id)
                raise ValidationError(_("The specified parent account does not exist."))

            if not parent_partner.is_account:
                _logger.error("The parent record must be an account. ID: %s, is_account: %s", parent_id, parent_partner.is_account)
                raise ValidationError(_("The parent record must be an account."))

            # Generate affiliate customer_code
            vals["customer_code"] = self._generate_reference(parent_partner.customer_code)
            _logger.debug("Assigned affiliate customer_code: %s for partner with parent %s", vals["customer_code"], parent_id)

        # Proceed with standard creation
        new_partner = super(Partner, self).create(vals)
        _logger.info("Partner created successfully with ID: %s", new_partner.id)
        
        return new_partner

    
    # @api.model
    # def create(self, vals):
    #     """
    #     Handles partner creation, including validation, customer code generation, 
    #     and partner type inheritance logic. Allows creation of Affiliates without a parent 
    #     during default initialization.
    #     """
    #     _logger.debug("Creating a new partner with vals: %s", vals)

    #     if vals.get("partner_type_code") == "AFFILIATE" and not vals.get("parent_id"):
    #         if self.env.context.get("default_partner_type_code") == "AFFILIATE":
    #             _logger.info("Creating an Affiliate without a parent during default initialization.")
    #             return super(Partner, self).create(vals)

    #     if vals.get("is_affiliate"):
    #         _logger.debug("Checking parent_id: %s", vals.get("parent_id"))
    #         parent_id = vals.get("parent_id")
    #         if not parent_id:
    #             _logger.error("Affiliates must have a parent account. Parent ID is missing!")
    #             raise ValidationError(_("Affiliates must have a parent account."))

    #         parent_partner = self.browse(parent_id)
    #         _logger.debug("Parent partner found: %s", parent_partner)

    #         if not parent_partner.exists():
    #             _logger.error("The specified parent account does not exist. ID: %s", parent_id)
    #             raise ValidationError(_("The specified parent account does not exist."))
    #         if not parent_partner.is_account:
    #             _logger.error("The parent record must be an account. ID: %s, is_account: %s", parent_id, parent_partner.is_account)
    #             raise ValidationError(_("The parent record must be an account."))

    #         vals["customer_code"] = self._generate_reference(vals)

    #         _logger.debug(f"Assigned affiliate customer_code: {vals['customer_code']} for partner with parent {parent_id}")

    #     partner_type_id = vals.get('partner_type_id')
    #     if partner_type_id:
    #         _logger.info("Partner type ID provided: %s", partner_type_id)
    #         partner_type = self.env['res.partner.type'].browse(partner_type_id)
    #         if partner_type:
    #             _logger.info("Found partner type: %s", partner_type.name)
    #             try:
    #                 inherit_values = self._get_inherit_values(partner_type)
    #                 _logger.debug("Inheritance values to update: %s", inherit_values)
    #                 vals.update(inherit_values)
    #             except Exception as e:
    #                 _logger.error("Error while retrieving inheritance values: %s", str(e))
    #                 raise
    #         else:
    #             _logger.warning("No partner type found with ID: %s", partner_type_id)

    #     if not vals.get("customer_code"):
    #         try:
    #             vals["customer_code"] = self._generate_reference(vals)
    #             _logger.info("Generated customer_code: %s", vals["customer_code"])
    #         except Exception as e:
    #             _logger.error("Error while generating customer_code: %s", str(e))
    #             raise

    #     legacy_customer_code = vals.get("legacy_customer_code")
    #     if legacy_customer_code:
    #         _logger.info("Checking legacy customer code: %s", legacy_customer_code)
    #         if self.search([("legacy_customer_code", "=", legacy_customer_code)]):
    #             _logger.error("Legacy Customer Code %s is not unique!", legacy_customer_code)
    #             raise ValidationError(_("Legacy Customer Code must be unique."))
    #         vals["legacy_customer_code"] = legacy_customer_code
    #         _logger.info("Legacy customer code retained: %s", legacy_customer_code)

    #     try:
    #         new_partner = super(Partner, self).create(vals)
    #         new_partner._validate_affiliate_parent()
    #         _logger.info("Partner created successfully with ID: %s", new_partner.id)
    #     except Exception as e:
    #         _logger.error("Error while creating partner: %s", str(e))
    #         raise

    #     try:
    #         new_partner._update_children(vals)
    #         _logger.info("Children updated successfully for partner ID: %s", new_partner.id)
    #     except Exception as e:
    #         _logger.error("Error while updating children: %s", str(e))
    #         raise

    #     _logger.info("Partner creation completed for ID: %s with customer code: %s", new_partner.id, new_partner.customer_code)
    #     return new_partner

    def write(self, vals):
        """
        Handles updates to partner records, including:
        - Updating values based on partner type inheritance.
        - Validating and updating legacy_customer_code.
        - Regenerating customer_code if parent or type changes.
        """
        _logger.info("Updating partner(s) with values: %s", vals)
        
        # Handle updates to partner_type_id
        partners_by_type = {}
        if vals.get('partner_type_id'):
            partner_type = self.env['res.partner.type'].browse(vals['partner_type_id'])
            partners_by_type[partner_type] = self
        else:
            for partner in self:
                partners_by_type.setdefault(partner.partner_type_id, self.browse())
                partners_by_type[partner.partner_type_id] |= partner

        # Apply inheritance logic for partner type
        for partner_type, partners in partners_by_type.items():
            if list(vals.keys()) != ['is_company']:  # Avoid infinite loop
                vals.update(self._get_inherit_values(partner_type, not_null=True))
        
        # Validate and update legacy_customer_code if provided
        if "legacy_customer_code" in vals:
            legacy_customer_code = vals.get("legacy_customer_code")
            _logger.info("Validating new legacy_customer_code: %s", legacy_customer_code)
            if self.search([("legacy_customer_code", "=", legacy_customer_code)]):
                _logger.error("Legacy Customer Code %s is not unique!", legacy_customer_code)
                raise ValidationError(_("Legacy Customer Code must be unique."))

        # Regenerate customer_code if parent_id or type-related fields are updated
        if "parent_id" in vals or any(key in vals for key in ["is_account", "is_affiliate", "is_contact", "is_patient"]):
            for partner in self:
                _logger.info("Regenerating customer_code for partner ID: %s", partner.id)
                vals["customer_code"] = self._generate_reference(vals)
                _logger.info("Updated customer_code: %s", vals["customer_code"])

        # Call the super method to perform the actual write operation
        result = super(Partner, self).write(vals)

        # Perform validation
        self._validate_affiliate_parent()

        # Update children if applicable
        self._update_children(vals)

        _logger.info("Partner(s) updated successfully.")
        return result

    # Ensure `_generate_reference` uses the sequence value
    def _generate_reference(self, vals):
        """
        Custom customer_code generation logic integrated with sequence.
        """
        _logger.debug("Generating reference with vals: %s", vals)

        # ✅ If vals is a string, return it directly
        if isinstance(vals, str):
            _logger.warning("Received pre-generated customer_code: %s", vals)
            return vals  # Just return it since it's already set

        # Ensure vals is a dictionary
        if not isinstance(vals, dict):
            _logger.error("Invalid data type for reference generation. Expected dict, got: %s", type(vals))
            raise ValidationError(_("Invalid data passed for reference generation."))

        # ✅ Generate for accounts
        if vals.get("is_account"):
            new_code = self.env["ir.sequence"].next_by_code("res.partner.account")
            if not new_code:
                raise ValidationError(_("Unable to generate sequence for accounts."))
            return new_code

        # ✅ Generate for affiliates
        elif vals.get("is_affiliate"):
            parent_id = vals.get("parent_id")

            # ✅ FIX: If parent_id is missing, try fetching it from the existing record
            if not parent_id and self.id:
                _logger.debug("Fetching parent_id from existing record.")
                parent_id = self.parent_id.id

            if not parent_id:
                _logger.error("Affiliates must have a parent account.")
                raise ValidationError(_("Affiliates must have a parent account."))

            parent = self.env['res.partner'].browse(parent_id)
            _logger.debug("Fetched Parent for Reference: %s", parent)

            if not parent.exists():
                _logger.error("The specified parent account does not exist.")
                raise ValidationError(_("The specified parent account does not exist."))
            if not parent.is_account:
                _logger.error("The parent record must be an account.")
                raise ValidationError(_("The parent record must be an account."))

            # ✅ Use pre-generated customer_code if it exists
            if parent.customer_code:
                _logger.debug("Using existing parent customer_code: %s", parent.customer_code)
                affiliate_number = str(self.sequence).zfill(2)  # Pad to 2 digits
                return f"{parent.customer_code}{affiliate_number}"
            else:
                raise ValidationError(_("Parent account has no customer_code."))

        # ✅ Generate for contacts
        elif vals.get("is_contact"):
            new_code = self.env["ir.sequence"].next_by_code("res.partner.contact")
            if not new_code:
                raise ValidationError(_("Unable to generate sequence for contacts."))
            return new_code

        # ✅ Generate for patients
        elif vals.get("is_patient"):
            new_code = self.env["ir.sequence"].next_by_code("res.partner.patient")
            if not new_code:
                raise ValidationError(_("Unable to generate sequence for patients."))
            return new_code

        # ✅ Catch-all for unsupported cases
        _logger.error("Unable to determine customer code sequence.")
        raise ValidationError(_("Unable to determine customer code sequence."))

   
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

