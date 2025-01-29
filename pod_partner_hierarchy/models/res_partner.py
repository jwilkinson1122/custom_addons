# -*- coding: utf-8 -*-

import logging
import json
from lxml import etree
from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

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
    
    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
    customer = fields.Boolean(string='Is a Customer', default=True, help="Check if this contact is a customer.")
    supplier = fields.Boolean(string='Is a Vendor', help="Check if this contact is a vendor.")
    commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Mark as True if this partner acts as its own trading company, even with a parent company."
    )
    # Field Declarations
    fax_number = fields.Char(string="Fax")
    # ref = fields.Char("ID", readonly=True, default=lambda self: _("New"))
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

    contact_address_type = fields.Selection(
        selection=[
            ("contact", "Contact Address"),
            ("patient", "Patient Address"),
        ],
        compute="_compute_contact_address_type",
        string="Contact Address Type",
        default="contact",
        required=False,
    )

    # Affiliate Fields
     # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True), ("is_affiliate", "=", True)],
    )

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

    @api.depends('partner_type_id')
    def _compute_partner_type_infos(self):
        """Compute parent-related fields based on partner type."""
        for partner in self:
            partner.can_have_parent = True
            partner.parent_is_required = False
            if partner.partner_type_id and partner.partner_type_id.can_have_parent:
                partner.can_have_parent = True
                partner.parent_is_required = partner.partner_type_id.parent_is_required

    @api.depends("type")
    def _compute_company_address_type(self):
        for record in self:
            record.company_address_type = record.type if record.type in dict(self._fields["company_address_type"].selection) else False

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
    @api.constrains('parent_id')
    def _check_no_circular_reference(self):
        for partner in self:
            if partner.parent_id and partner.parent_id.id == partner.id:
                raise ValidationError(_("A partner cannot be its own parent."))

            visited = set()
            current = partner.parent_id
            while current:
                if current.id in visited:
                    raise ValidationError(_("Circular reference detected in the hierarchy."))
                visited.add(current.id)
                current = current.parent_id

    # Onchange Methods
    @api.onchange('company_type')
    def _onchange_company_type(self):
        type_mapping = {
            'company': 'ACCOUNT' if self.is_account else 'AFFILIATE',
            'person': 'PATIENT' if self.is_patient else 'CONTACT',
        }
        code = type_mapping.get(self.company_type, 'CONTACT')
        self.partner_type_id = self.env['res.partner.type'].search([('code', '=', code)], limit=1)


    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        self.apply_contact_logic()
        domain = [("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))
        return {"domain": {"responsible_contact_id": domain}}

    def apply_contact_logic(self):
        if self.parent_id:
            contacts = self.env["res.partner"].search([
                ("parent_id", "=", self.parent_id.id),
                ("is_company", "=", False)
            ])
            if contacts:
                self.responsible_contact_id = contacts[0]

 
    @api.model
    def create(self, vals):
        """
        Handles customer code generation during record creation and retains legacy_customer_code if provided.
        """
        _logger.info("Creating a new partner with values: %s", vals)

        # Generate the new customer code using standard sequence logic
        vals["customer_code"] = self._generate_reference(vals)
        _logger.info("Generated customer code: %s", vals["customer_code"])

        # Retain the legacy code if provided
        legacy_customer_code = vals.get("legacy_customer_code")
        if legacy_customer_code:
            _logger.info("Checking legacy customer code: %s", legacy_customer_code)
            # Validate that it's unique within the system
            if self.search([("legacy_customer_code", "=", legacy_customer_code)]):
                _logger.error("Legacy Customer Code %s is not unique!", legacy_customer_code)
                raise ValidationError(_("Legacy Customer Code must be unique."))
            vals["legacy_customer_code"] = legacy_customer_code
            _logger.info("Legacy customer code retained: %s", legacy_customer_code)

        partner = super(ResPartner, self).create(vals)
        _logger.info("Partner created successfully with ID: %s and customer code: %s", partner.id, partner.customer_code)
        return partner

    def write(self, vals):
        """
        Handles updates to legacy_customer_code and regenerates customer_code if type or parent changes.
        """
        _logger.info("Updating partner(s) with values: %s", vals)

        if "legacy_customer_code" in vals:
            legacy_customer_code = vals.get("legacy_customer_code")
            _logger.info("Validating new legacy customer code: %s", legacy_customer_code)
            # Validate that the new legacy code is unique
            if self.search([("legacy_customer_code", "=", legacy_customer_code)]):
                _logger.error("Legacy Customer Code %s is not unique!", legacy_customer_code)
                raise ValidationError(_("Legacy Customer Code must be unique."))
        
        if "parent_id" in vals or any(key in vals for key in ["is_account", "is_affiliate", "is_contact", "is_patient"]):
            for partner in self:
                _logger.info("Regenerating customer code for partner ID: %s", partner.id)
                vals["customer_code"] = self._generate_reference(vals)
                _logger.info("Updated customer code: %s", vals["customer_code"])

        result = super(ResPartner, self).write(vals)
        _logger.info("Partner(s) updated successfully.")
        return result

    def _generate_reference(self, vals):
        """
        Generate a new customer code based on the partner type and parent relationship.
        """
        _logger.info("Generating customer code for values: %s", vals)

        sequence_code = None
        if vals.get("is_account"):
            sequence_code = "res.partner.account"
        elif vals.get("is_affiliate"):
            sequence_code = "res.partner.affiliate"
        elif vals.get("is_contact"):
            sequence_code = "res.partner.contact"
        elif vals.get("is_patient"):
            sequence_code = "res.partner.patient"

        if not sequence_code:
            _logger.error("Unable to determine sequence type for values: %s", vals)
            raise ValidationError(_("Unable to determine sequence type for this partner."))

        # Generate the sequence-based code
        new_code = self.env["ir.sequence"].next_by_code(sequence_code)
        _logger.info("Generated sequence-based code: %s", new_code)

        # Append the parent reference for affiliates
        if vals.get("is_affiliate") and vals.get("parent_id"):
            parent = self.browse(vals["parent_id"])
            if not parent.customer_code:
                _logger.error("Parent must have a customer code assigned. Parent ID: %s", parent.id)
                raise ValidationError(_("Parent must have a customer code assigned."))

            # Use only the suffix from the affiliate sequence
            affiliate_suffix = new_code[len("AF"):]  # Strip the "AF" prefix to get the padded suffix
            new_code = f"{parent.customer_code}/AF{affiliate_suffix}"
            _logger.info("Affiliate customer code generated: %s", new_code)

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