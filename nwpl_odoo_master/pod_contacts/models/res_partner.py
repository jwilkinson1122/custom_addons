import traceback
import logging
import base64
import json
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import Command, _, models, fields, tools, api, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError, RedirectWarning
from odoo.modules.module import get_module_resource
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval
from .res_partner_contact_point_mixin import CONTACT_POINT_TYPES

_logger = logging.getLogger(__name__)


INVOICE = "invoice"
ADDRESS_FIELDS = ("street", "street2", "city", "zip", "state_id", "country_id")


class Partner(models.Model):
    _inherit = ["multi.company.abstract", "incrementing.sequence.mixin", "res.partner"]
    _name = "res.partner"
    _sequence_group = "parent_id"
    # _inherit = "res.partner"
    
    # _sql_constraints = [
    #     ('single_type_check', "CHECK((is_account::int + is_affiliate::int + is_contact::int + is_patient::int) = 1)", "Partner must belong to exactly one category."),
    # ]
    # _sql_constraints = [
    #     ('customer_code_unique', 'unique(customer_code)', 'Customer Code must be unique.'),
    # ]

    # Boolean Fields
    is_new_record = fields.Boolean(compute="_compute_is_new_record", store=False)
    is_supplier = fields.Boolean(string="Supplier", default=False)
    is_partner = fields.Boolean(string="Partner", default=False)
    is_account = fields.Boolean(string="Account", default=False)
    is_affiliate = fields.Boolean(
        string="Affiliate", help="Check this box if this is a Company Affiliate."
    )
    is_commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Set this to True if this contact should be treated as its own trading company, "
        "even if it has a parent company.",
    )
    is_contact = fields.Boolean(
        string="Contact", help="Check this box if this is a Company Contact."
    )
    is_patient = fields.Boolean(
        string="Patient", help="Check this box if this is a Patient."
    )
    can_have_parent = fields.Boolean(compute="_compute_partner_type_infos")
    parent_is_required = fields.Boolean(compute="_compute_partner_type_infos")

    use_parent_invoice_address = fields.Boolean(
        string="Use Parent Invoice Address", default=False
    )
    use_parent_shipping_address = fields.Boolean(
        string="Use Parent Shipping Address", default=False
    )
    use_patient_shipping_address = fields.Boolean(
        string="Use Patient Shipping Address", default=False
    )

    ref = fields.Char(string="Ref", index=True)
    # customer_code = fields.Char(
    #     string="Customer ID", readonly=True, default=lambda self: _("New")
    # )
    customer_code = fields.Char(
        string="Customer Code",
        copy=False,
        index=True,
        default=lambda self: _("New"),  
        readonly=True,
    )
    
    
    
    # legacy_customer_code = fields.Char("Legacy ID", readonly=True)
    legacy_customer_code = fields.Char("Legacy ID")
    partner_company_type = fields.Many2one(
        comodel_name="res.partner.company.type",
        help="Specify the type of company this belongs to.",
    )
    partner_relation_label = fields.Char(
        "Partner relation label", translate=True, default="Attached To:", readonly=True
    )
    parent_type_ids = fields.Many2many(
        "res.partner.type",
        string="Company types authorized for parent",
        compute="_compute_parent_types",
    )
    partner_type_id = fields.Many2one(
        "res.partner.type", "Partner Type", help="Specify the type of partner."
    )
    partner_type_code = fields.Char(
        related="partner_type_id.code", store=True, readonly=True
    )
    parent_relation_label = fields.Char(
        related="partner_type_id.parent_relation_label", readonly=True
    )
    companies_label = fields.Char(
        related="partner_type_id.companies_label", readonly=True
    )
    contacts_label = fields.Char(
        related="partner_type_id.contacts_label", readonly=True
    )

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
        store=True,
        default=False,
    )

    company_address_type = fields.Selection(
        selection=[
            ("invoice", "Invoice"),
            ("delivery", "Delivery"),
            ("supplier", "Supplier"),
            ("other", "Other"),
        ],
        string="Type",
        compute="_compute_company_address_type",
        inverse="_inverse_company_address_type",
        store=True,
    )
    
    parent_id = fields.Many2one(
        "res.partner",
        index=True,
        domain="[('is_company', '=', True), '|', ('is_account', '=', True), ('is_affiliate', '=', True)]",
        string="Related Company",
    )

    parent_name = fields.Char(
        related="parent_id.name", readonly=True, string="Account Name"
    )

    previous_parent_id = fields.Many2one(
        "res.partner", string="Previous Parent", help="Stores the last assigned parent."
    )

    is_merged = fields.Boolean(
        string="Merged",
        default=False,
        help="Indicates if this partner was merged into another.",
    )

    merged_into_id = fields.Many2one(
        "res.partner",
        string="Merged Into",
        help="If this affiliate was merged, this stores the new parent.",
    )

    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_affiliate", "=", True)],
    )

    affiliates_count = fields.Integer(
        "Number of Affiliates", compute="_compute_affiliates_count", compute_sudo=True
    )

    sub_affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Affiliates",
        compute="_compute_sub_affiliate_ids",
        help="Indirectly associated affiliates (grandchildren).",
    )

    sub_affiliates_count = fields.Integer(
        "Number of Sub-Affiliates",
        compute="_compute_sub_affiliates_count",
        compute_sudo=True,
    )

    # contacts
    child_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="parent_id",
        domain=[
            ("active", "=", True),
            ("is_company", "=", False),
            ("is_contact", "=", True),  # Ensure only contacts are included
            ("is_patient", "=", False),  # Explicitly exclude patients
        ],
        string="Contacts",
    )

    contact_id = fields.Many2one(
        "res.partner",
        string="Related Contact",
        domain=[("is_contact", "=", True)],
        help="Link to the related contact.",
    )

    sub_contact_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Contacts",
        compute="_compute_sub_contact_ids",
        help="Indirectly associated contacts (grandchildren).",
    )

    contacts_count = fields.Integer(
        "Number of Contacts", compute="_compute_contacts_count"
    )

    sub_contacts_count = fields.Integer(
        "Number of Sub-Contacts", compute="_compute_sub_contacts_count"
    )

    primary_contact_id = fields.Many2one(
        "res.partner",
        string="Contact",
        domain="[('parent_id', '=', parent_id), ('is_contact', '=', True), ('is_company', '=', False)]",
        context={"primary_contact_selection": True},
    )

    contact_role_ids = fields.Many2many(string="Roles", comodel_name="res.partner.role")

    department_id = fields.Many2one("res.partner.contact.department", "Department")

    contact_point_ids = fields.One2many(
        "res.partner.contact_point", "partner_id", "Contact Points"
    )
    
    email = fields.Char(
        compute="_compute_contact_points", inverse="_set_email", store=True
    )
    
    phone = fields.Char(
        compute="_compute_contact_points", inverse="_set_phone", store=True
    )
    
    mobile = fields.Char(
        compute="_compute_contact_points", inverse="_set_mobile", store=True
    )
    
    fax_number = fields.Char(string="Fax")

    document_ids = fields.One2many(
        "res.partner.document", "partner_id", string="Documents"
    )

    documents_count = fields.Integer(
        compute="_compute_total_documents_count",
        string="Document Count",
        help="Get the documents count",
    )
    
    @api.depends("document_ids")
    def _compute_total_documents_count(self):
        """Get the document count on smart tab"""
        for record in self:
            record.documents_count = self.env["ir.attachment"].search_count(
                [("res_id", "=", record.id), ("res_model", "=", "res.partner")]
            )

    def action_partner_documents(self):
        """Return the documents of corresponding partner in the smart tab"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Documents",
            "view_mode": "kanban,form",
            "res_model": "ir.attachment",
            "domain": [("res_id", "=", self.id), ("res_model", "=", "res.partner")],
            "context": {"create": False},
        }

    # Contact Points            
    @api.depends("contact_point_ids.name", "contact_point_ids.is_default", "contact_point_ids.contact_point_type")
    def _compute_contact_points(self):
        for partner in self:
            for cptype, _label in CONTACT_POINT_TYPES:
                # always pick at most one default
                default_cp = partner.contact_point_ids.filtered(
                    lambda cp: cp.contact_point_type == cptype and cp.is_default
                )[:1]
                partner[cptype] = default_cp.name if default_cp else False

    def _set_contact_point(self, contact_point_type):
        """Multi-safe inverse: for each partner, make sure the typed value exists as a contact point
        and is flagged as default, unflagging other defaults of the same type."""
        ContactPoint = self.env["res.partner.contact_point"]
        for partner in self:
            value = partner[contact_point_type]
            if not value:
                continue

            # exact match on this partner & type
            existing = partner.contact_point_ids.filtered(
                lambda cp: cp.contact_point_type == contact_point_type and cp.name == value
            )

            if existing:
                # ensure it's default, and unset defaults on others of the same type
                if not existing[0].is_default:
                    existing[0].is_default = True
                others = (partner.contact_point_ids - existing).filtered(
                    lambda cp: cp.contact_point_type == contact_point_type and cp.is_default
                )
                if others:
                    others.write({"is_default": False})
            else:
                # create new as default and unset any previous default of same type
                others = partner.contact_point_ids.filtered(
                    lambda cp: cp.contact_point_type == contact_point_type and cp.is_default
                )
                if others:
                    others.write({"is_default": False})
                ContactPoint.create({
                    "name": value,
                    "partner_id": partner.id,
                    "contact_point_type": contact_point_type,
                    "is_default": True,
                })

    def get_fields_contact_points(self):
        return {"phone", "mobile", "email"}

    def _set_email(self):
        for partner in self:
            partner._set_contact_point("email")

    def _set_phone(self):
        for partner in self:
            partner._set_contact_point("phone")

    def _set_mobile(self):
        for partner in self:
            partner._set_contact_point("mobile")

    def action_show_contact_points(self):
        contact_point_type = self._context.get("default_contact_point_type")
        partner_id = self._context.get("default_partner_id")
        return {
            "name": "%ss" % dict(CONTACT_POINT_TYPES).get(contact_point_type),
            "type": "ir.actions.act_window",
            "res_model": "res.partner.contact_point",
            "view_mode": "tree",
            "view_id": False,
            "domain": [
                ("contact_point_type", "=", contact_point_type),
                ("partner_id", "=", partner_id),
            ],
            "context": dict(self._context),
        }


    def _compute_is_new_record(self):
        for record in self:
            record.is_new_record = not bool(
                record._origin.id
            )  # Check if the record has an ID

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get("is_affiliate") and not res.get("parent_id"):
            res["parent_id"] = False
        if res.get('is_supplier') and not res.get('company_address_type'):
            res['company_address_type'] = 'supplier'
        return res

    # Generic Count Computation
    def _compute_count(self, related_field, count_field, filters=None):
        for record in self:
            related_records = getattr(record, related_field)
            if filters:
                related_records = related_records.filtered(filters)
            setattr(record, count_field, len(related_records))

    # Affiliates
    @api.depends("affiliate_ids")
    def _compute_affiliates_count(self):
        self._compute_count(
            "affiliate_ids",
            "affiliates_count",
            filters=lambda r: r.is_affiliate and r.is_company and not r.is_account,
        )

    def _get_all_sub_affiliates(self):
        """Recursively find all indirect affiliates"""
        sub_affiliates = self.env["res.partner"]
        for affiliate in self.affiliate_ids:
            sub_affiliates |= (
                affiliate.affiliate_ids | affiliate._get_all_sub_affiliates()
            )
        return sub_affiliates

    @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
    def _compute_sub_affiliate_ids(self):
        """Compute all indirect affiliates"""
        for partner in self:
            direct_affiliates = partner.affiliate_ids  # Direct affiliates
            all_sub_affiliates = (
                partner._get_all_sub_affiliates()
            )  # Indirect affiliates
            partner.sub_affiliate_ids = all_sub_affiliates - direct_affiliates

    @api.depends("sub_affiliate_ids")
    def _compute_sub_affiliates_count(self):
        """Compute the count of sub-affiliates."""
        for record in self:
            record.sub_affiliates_count = len(record.sub_affiliate_ids)

    # Contacts
    @api.depends("child_ids")
    def _compute_contacts_count(self):
        for record in self:
            contacts = record.child_ids.filtered(
                lambda r: r.is_contact and not r.is_patient and not r.is_company
            )

            _logger.info("Computing contacts count for: %s", record.name)
            _logger.info("Contacts found: %s", contacts.mapped("name"))
            _logger.info(
                "Contacts incorrectly counted: %s",
                record.child_ids.filtered(lambda r: r.is_contact).mapped("name"),
            )

            record.contacts_count = len(contacts)

    def _get_all_sub_contacts(self):
        sub_contacts = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if not child.is_company and not child.is_patient:
                    sub_contacts |= child
                sub_contacts |= child._get_all_sub_contacts()
        return sub_contacts

    @api.depends("affiliate_ids", "affiliate_ids.child_ids")
    def _compute_sub_contact_ids(self):
        for partner in self:
            all_sub_contacts = self.env["res.partner"]

            def get_indirect_contacts(partner):
                nonlocal all_sub_contacts
                for affiliate in partner.affiliate_ids:
                    all_sub_contacts |= affiliate.child_ids.filtered(
                        lambda r: r.is_contact
                        and not r.is_account
                        and not r.is_company
                        and not r.is_patient
                    )
                    get_indirect_contacts(affiliate)

            get_indirect_contacts(partner)
            partner.sub_contact_ids = all_sub_contacts

    @api.depends("sub_contact_ids")
    def _compute_sub_contacts_count(self):
        """Compute the count of sub-contacts."""
        for record in self:
            record.sub_contacts_count = len(record.sub_contact_ids)

    # Patients
        patient_id = fields.Many2one(
        "res.partner",
        string="Related Contact",
        domain=[("is_patient", "=", True)],
        help="Link to the related patient.",
    )

    # Patients
    patient_ids = fields.One2many(
        "res.partner", "parent_id", domain=[("is_patient", "=", True)]
    )
    
    sub_patient_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Patients",
        compute="_compute_sub_patient_ids",
    )
    patients_count = fields.Integer(
        "Number of Patients", compute="_compute_patients_count"
    )

    photo = fields.Binary(string="Picture")
    image1 = fields.Binary("Right Photo")
    image2 = fields.Binary("Left Photo")
    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char("Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char("Right Obj File Name")

    height = fields.Integer("Height", store=True, copy=True)
    weight = fields.Float("Weight", store=True, copy=True)
    shoe_size = fields.Float("Shoe Size", store=True, copy=True)
    shoe_type = fields.Selection([
        ('dress', 'Dress'), ('casual', 'Casual'),
        ('athletic', 'Athletic'), ('other', 'Other')
    ], string='Shoe Type')
    shoe_width = fields.Selection([
        ("wide", "Wide"), ("xwide", "Extra Wide"), ("narrow", "Narrow")
    ], string="Shoe Width")

    gender = fields.Selection([
        ("male", "Male"), ("female", "Female"), ("other", "Other")
    ], string="Gender")
    birth_date = fields.Date("DOB")
    patient_age = fields.Integer("Age", compute="_compute_age", store=True)
    notes = fields.Text("Notes")

    patient_flag_ids = fields.One2many("res.partner.flag", "patient_id", string="Flags")
    patient_flag_count = fields.Integer("Flag Count", compute="_compute_flag_count")
    
    image1 = fields.Binary("Right photo")
    image2 = fields.Binary("Left photo")
    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")
    
    # measurement_ids = fields.One2many('pod.measurement.group', 'partner_id', 'Measurement')


    @api.depends('birth_date')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.birth_date:
                rec.patient_age = relativedelta(today, rec.birth_date).years
            else:
                rec.patient_age = 0

    @api.depends('patient_flag_ids')
    def _compute_flag_count(self):
        for rec in self:
            rec.patient_flag_count = len(rec.patient_flag_ids)
            
    @api.depends("patient_ids")
    def _compute_patients_count(self):
        self._compute_count("patient_ids", "patients_count")

    def _get_all_sub_patients(self):
        sub_patients = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if child.is_patient:
                    sub_patients |= child
                sub_patients |= child._get_all_sub_patients()
        return sub_patients

    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_patient_ids(self):
        for partner in self:
            all_sub_patients = partner._get_all_sub_patients()
            partner.sub_patient_ids = all_sub_patients - partner.patient_ids

    # def add_measurement_category(self, measurement_values):
    #     """Create measurement categories and measurements based on provided values."""
    #     if isinstance(measurement_values, str):
    #         try:
    #             measurement_values = json.loads(measurement_values)
    #         except json.JSONDecodeError:
    #             raise ValidationError("Invalid JSON format")

    #     if not isinstance(measurement_values, list) or not measurement_values:
    #         raise ValidationError("Invalid data format; list of dictionaries expected.")

    #     required_keys = {'date', 'category_id', 'measurement_unit', 'measurement_ids'}
    #     for values in measurement_values:
    #         if not required_keys.issubset(values.keys()):
    #             missing = required_keys - set(values.keys())
    #             raise ValidationError(f"Missing required keys: {', '.join(missing)}")

    #         measurement_cat = self.env['pod.measurement.group'].create({
    #             'date': values.get('date'),
    #             'partner_id': self.id,
    #             'category_id': values.get('category_id'),
    #             'measurement_unit': int(values.get('measurement_unit'))
    #         })

    #         if measurement_cat:
    #             measurements = [
    #                 {
    #                     'measurement_cat_id': measurement_cat.id,
    #                     'measurement_type': m.get('measurement_type'),
    #                     'measurement': m.get('measurement_value')
    #                 }
    #                 for m in values.get('measurement_ids', [])
    #             ]
    #             self.env['measurement.measurement'].create(measurements)

    # def get_measurements(self):
    #     measurements = []
    #     for record in self:
    #         measurement_lines = self.env['pod.measurement.group'].search([('partner_id', '=', record.id)])
    #         for line in measurement_lines:
    #             measurements.append({
    #                 'date': line.date,
    #                 'category': line.category_id.name,
    #                 'unit': line.measurement_unit.name,
    #                 'values': [{'id': m.id, 'name': m.measurement_type.name, 'value': m.measurement} for m in line.measurement_ids]
    #             })
    #     return measurements

    # Compute and Inverse Methods
    
    
    
    
    @api.depends("type")
    def _compute_company_address_type(self):
        for record in self:
            if not record.company_address_type:  #  Only set if empty
                if record.type in dict(self._fields["company_address_type"].selection):
                    record.company_address_type = record.type
                else:
                    record.company_address_type = False  #  Keep it empty if not set

    def _inverse_company_address_type(self):
        for record in self:
            if record.company_address_type:
                record.type = record.company_address_type

    @api.depends("partner_type_id")
    def _compute_parent_types(self):
        for partner in self:
            if partner.partner_type_id:
                partner.parent_type_ids = partner.partner_type_id.parent_type_ids
            else:
                partner.parent_type_ids = self.env["res.partner.type"].browse()

    @api.depends("partner_type_id")
    def _compute_partner_type_infos(self):
        for partner in self:
            partner.can_have_parent = partner.partner_type_id.can_have_parent
            partner.parent_is_required = partner.partner_type_id.parent_is_required

    @api.constrains("parent_id", "is_affiliate")
    def _check_affiliate_parent_constraint(self):
        for record in self:
            if record.is_affiliate and not record.parent_id:
                if record.create_date:  # Ensure the record has been saved
                    raise ValidationError(_("Affiliates must have a parent account."))

    # Onchange Methods
    
    @api.onchange('is_supplier', 'company_type')
    def _onchange_supplier_default_address_type(self):
        for p in self:
            if p.is_supplier and p.is_company and not p.company_address_type:
                p.company_address_type = 'supplier'
            
    @api.onchange("company_type")
    def _onchange_company_type(self):
        """Update partner_type_id based on the selected company_type using boolean fields."""
        if self.company_type == "company":
            partner_type_field = "is_account" if self.is_account else "is_affiliate"
        elif self.company_type == "person":
            partner_type_field = "is_patient" if self.is_patient else "is_contact"
        else:
            partner_type_field = "is_contact"  # Default fallback
        self.partner_type_id = self.env["res.partner.type"].search(
            [(partner_type_field, "=", True)], limit=1
        )

    @api.onchange("partner_type_id")
    def _onchange_partner_type(self):
        if not self.partner_type_id:
            return

        # Apply inherited field values
        self.update(self._get_inherit_values(self.partner_type_id))

        # Normalize the `type` field from the partner type (if valid)
        type_selection = dict(self._fields["type"].selection)
        selected_type = self.partner_type_id.type if self.partner_type_id.type in type_selection else False

        # Apply boolean flags and type
        is_person_type = self.partner_type_id.company_type == "person"
        is_contact_type = selected_type == "contact"

        self.is_contact = is_person_type and is_contact_type
        self.is_company = not self.is_contact
        self.type = False if self.is_contact else selected_type
        
        
        
    def _clear_address_fields(self):
        for f in ADDRESS_FIELDS:
            self[f] = False    


    @api.onchange('parent_id')
    def onchange_parent_id(self):
        """
        One unified handler that:
        • Skips base address prefill for Affiliates unless user opted in with
            use_parent_invoice_address/use_parent_shipping_address (or context guard).
        • Keeps your primary_contact domain and customer_code/previous_parent_id handling.
        • Lets base behavior run for non-Affiliates (or opted-in Affiliates).
        """
        self.ensure_one()

        # Decide whether to bypass base's address copy
        skip_prefill = (
            (self.is_affiliate and not (self.use_parent_invoice_address or self.use_parent_shipping_address))
            or self.env.context.get('no_address_prefill')
        )

        # Call base onchange only when we do NOT want to skip prefill
        if self.parent_id and not skip_prefill:
            super(Partner, self).onchange_parent_id()

        # ---- Your logic (always applied) ---------------------------------------
        # Primary contact selection
        self.apply_contact_logic()

        # Domain for primary_contact_id
        domain = [("is_contact", "=", True), ("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))

            # Customer code + previous_parent tracking
            if self.previous_parent_id and self.previous_parent_id != self.parent_id:
                _logger.info(
                    "Reassigning parent for %s from %s to %s",
                    self.name,
                    self.previous_parent_id.name,
                    self.parent_id.name,
                )
                if self.customer_code and self.customer_code != _("New"):
                    self.legacy_customer_code = self.customer_code

                # Generate using your role-aware method
                self.customer_code = self._generate_customer_code({
                    "parent_id": self.parent_id.id,
                    "is_account": self.is_account,
                    "is_affiliate": self.is_affiliate,
                    "is_contact": self.is_contact,
                    "is_patient": self.is_patient,
                })
                self._update_related_records()

            # Store current as previous
            self.previous_parent_id = self.parent_id

            # ---- Address behavior ----------------------------------------------
            if self.is_affiliate:
                # Default: no prefill. Only copy if user opted in via the flags.
                if self.use_parent_invoice_address or self.use_parent_shipping_address:
                    # Apply the chosen parent address
                    self._onchange_parent_address_flags()
                else:
                    # Make sure nothing auto-filled remains
                    self._clear_address_fields()
            else:
                # Non-Affiliates: base might have filled; respect flags too
                if self.use_parent_invoice_address or self.use_parent_shipping_address:
                    self._onchange_parent_address_flags()

        # Return domain for single-record form
        return {"domain": {"primary_contact_id": domain}}

    def apply_contact_logic(self):
        """Assigns primary contact based on parent."""
        if self.parent_id:
            contacts = self.env["res.partner"].search(
                [("parent_id", "=", self.parent_id.id), ("is_company", "=", False)],
                limit=1,
            )
            self.primary_contact_id = contacts.id if contacts else False
            _logger.debug(
                f"Assigned primary_contact_id: {contacts.name if contacts else 'None'}"
            )
        else:
            self.primary_contact_id = False

    def _get_inherit_values(self, partner_type, not_null=False):
        if not partner_type:
            return {}
        inherit_fields = getattr(
            partner_type, "_%s_inherit_fields" % partner_type.company_type
        )
        inherit_values = partner_type.read(inherit_fields)[0]
        if "id" in inherit_values:
            del inherit_values["id"]
        if not_null:
            for fname in list(inherit_values.keys()):
                if not inherit_values[fname]:
                    del inherit_values[fname]
        return inherit_values

    def _update_children(self, vals):
        for partner in self:
            if partner.child_ids and partner.partner_type_id.field_ids:
                children_vals = {
                    key: value
                    for key, value in vals.items()
                    if key in partner.partner_type_id.field_ids.mapped("name")
                }
                if children_vals:
                    partner.child_ids.write(children_vals)

    # Validation helper method
    def _validate_affiliate_parent(self):
        for record in self:
            if not record.id:  # Skip validation for new (unsaved) records
                continue
            if record.is_affiliate and not record.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))

    # Address Flags
    # @api.onchange("use_parent_invoice_address", "use_parent_shipping_address", "parent_id", "is_affiliate")
    # def _onchange_parent_address_flags(self):
    #     """Only copy when the user asks. Otherwise, keep blank."""
    #     for rec in self:
    #         if rec.use_parent_invoice_address and rec.use_parent_shipping_address:
    #             rec.use_parent_shipping_address = False

    #         if not rec.parent_id:
    #             continue

    #         if rec.is_affiliate:
    #             if rec.use_parent_invoice_address:
    #                 rec._apply_parent_address(address_type="invoice")
    #             elif rec.use_parent_shipping_address:
    #                 rec._apply_parent_address(address_type="shipping")
    #             else:
    #                 rec._clear_address_fields()
    #         else:
    #             if rec.use_parent_invoice_address:
    #                 rec._apply_parent_address(address_type="invoice")
    #             if rec.use_parent_shipping_address:
    #                 rec._apply_parent_address(address_type="shipping")
                

    def _address_is_empty(self):
        """True if all address fields are empty."""
        self.ensure_one()
        return not any(self[f] for f in ADDRESS_FIELDS)

    # def _apply_parent_address(self, address_type):
    #     address_fields = ["street", "street2", "city", "zip", "state_id", "country_id"]
    #     parent = self.parent_id

    #     if address_type == "invoice":
    #         _logger.debug(f"Applying parent invoice address from: {parent.name}")
    #     elif address_type == "shipping":
    #         _logger.debug(f"Applying parent shipping address from: {parent.name}")

    #     for field in address_fields:
    #         parent_value = getattr(parent, field, False)
    #         if field in ["state_id", "country_id"]:
    #             parent_value = parent_value.id if parent_value else False
    #         self[field] = parent_value
    
    def _apply_parent_address(self, address_type, *, replace=False):
        """
        Copy parent's address onto current record.
        - replace=False  → only fill empty fields (non-destructive)
        - replace=True   → overwrite everything
        Returns True if at least one field was written.
        """
        self.ensure_one()
        if not self.parent_id:
            return False

        parent = self.parent_id
        copied_any = False
        for field in ADDRESS_FIELDS:
            parent_val = getattr(parent, field, False)
            if field in ("state_id", "country_id"):
                parent_val = parent_val.id if parent_val else False
            if replace or not self[field]:
                self[field] = parent_val
                copied_any = True
        return copied_any

    @api.onchange("use_parent_invoice_address", "use_parent_shipping_address", "parent_id", "is_affiliate")
    def _onchange_parent_address_flags(self):
        """
        Affiliates: do nothing by default. If a flag is checked, *fill-only-blank* by default.
        Never clobber user input unless explicitly asked (replace=True).
        """
        warnings = []
        for rec in self:
            # make the flags mutually exclusive if you want
            if rec.use_parent_invoice_address and rec.use_parent_shipping_address:
                rec.use_parent_shipping_address = False

            if not rec.parent_id:
                continue

            # Default behavior: non-destructive copy (only fill empty fields)
            if rec.is_affiliate:
                if rec.use_parent_invoice_address:
                    wrote = rec._apply_parent_address("invoice", replace=False)
                    if not wrote and not rec._address_is_empty():
                        warnings.append(_("Parent invoice address not applied because fields already have values."))
                elif rec.use_parent_shipping_address:
                    wrote = rec._apply_parent_address("shipping", replace=False)
                    if not wrote and not rec._address_is_empty():
                        warnings.append(_("Parent shipping address not applied because fields already have values."))
                else:
                    # user opted out; keep whatever is on the form
                    pass
            else:
                # Non-affiliates: same non-destructive rule (or keep your previous behavior if preferred)
                if rec.use_parent_invoice_address:
                    rec._apply_parent_address("invoice", replace=False)
                if rec.use_parent_shipping_address:
                    rec._apply_parent_address("shipping", replace=False)

        if warnings:
            return {"warning": {"title": _("Address not replaced"), "message": "\n".join(warnings)}}
       
       
    def action_replace_with_parent_invoice(self):
        for rec in self.filtered(lambda r: r.parent_id):
            rec._apply_parent_address("invoice", replace=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": _("Address updated"),
                    "message": _("Invoice address replaced with parent’s."),
                    "type": "success"}
        }

    def action_replace_with_parent_shipping(self):
        for rec in self.filtered(lambda r: r.parent_id):
            rec._apply_parent_address("shipping", replace=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": _("Address updated"),
                    "message": _("Shipping address replaced with parent’s."),
                    "type": "success"}
        }

    
    # CRUD
    # --- Helpers --------------------------------------------------------------
    def _aff_base_code(self, parent):
        code = parent.customer_code or ""
        parts = code.split("-")
        return "-".join(parts[:2]) if len(parts) > 2 else code

    def _next_aff_suffix(self, parent):
        """Return the next numeric suffix for this parent, with a row lock to serialize."""
        # Lock the parent row so two concurrent transactions don’t hand out the same number
        self.env.cr.execute("SELECT id FROM res_partner WHERE id=%s FOR UPDATE", (parent.id,))
        # Read existing affiliate codes under this parent (visible in this tx)
        existing = self.env["res.partner"].sudo().search_read(
            [("parent_id", "=", parent.id), ("is_affiliate", "=", True), ("customer_code", "!=", False)],
            ["customer_code"]
        )
        max_n = 0
        for rec in existing:
            code = rec["customer_code"] or ""
            suffix = code.split("-")[-1]  # expect ...-NN at the end
            if suffix.isdigit():
                max_n = max(max_n, int(suffix))
        return max_n + 1

    def _assign_affiliate_codes_batch(self):
        """
        Assign unique customer_code to new affiliates that still have placeholder values,
        handing out sequential suffixes per parent in one go.
        """
        PLACEHOLDERS = {False, "", "/", _("New")}
        todo = self.filtered(lambda p: p.is_affiliate and (p.customer_code in PLACEHOLDERS))
        if not todo:
            return

        for parent in todo.mapped("parent_id"):
            children = todo.filtered(lambda p: p.parent_id == parent)
            if not parent or not parent.customer_code or not children:
                continue
            start = self._next_aff_suffix(parent)
            base = self._aff_base_code(parent)
            # Give 01, 02, 03... to this batch in a deterministic order
            for i, child in enumerate(children, start=start):
                child.with_context(_skip_customer_code_sync=True).write({"customer_code": f"{base}-{i:02d}"})


    # --- Overrides ------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """
        Keep 'New' while editing. After real create, assign codes:
        - Accounts via sequence (ID####)
        - Affiliates via parent-based increment (batch-safe)
        - Contacts/Patients via their sequences
        Also handles the case where affiliates are created on an unsaved Account:
        after assigning the Account code, we sweep its new affiliates and number them.
        """
        PLACEHOLDERS = {False, "", "/", _("New")}

        # Normalize incoming values but DO NOT pre-generate affiliate codes
        for vals in vals_list:
            _logger.info("[CREATE] Creating partner: %s", vals)
            self._amend_company_id(vals)

            # Inline child creation: default to contact if no role given
            if vals.get("parent_id") and not any(vals.get(f) for f in ("is_affiliate", "is_account", "is_patient", "is_contact")):
                vals["is_contact"] = True
                vals.setdefault("is_company", False)
                vals.setdefault("company_type", "person")

            # Role enforcement
            role_flags = ("is_affiliate", "is_contact", "is_account", "is_patient")
            if any(vals.get(flag) for flag in role_flags):
                if vals.get("is_patient"):
                    vals.update({"is_company": False, "is_affiliate": False, "is_account": False, "is_contact": False, "company_type": "person"})
                elif vals.get("is_contact"):
                    vals.update({"is_company": False, "is_affiliate": False, "is_account": False, "is_patient": False, "company_type": "person"})
                elif vals.get("is_affiliate"):
                    vals.update({"is_company": True, "is_account": False, "is_contact": False, "is_patient": False, "company_type": "company"})
                else:
                    vals.setdefault("company_type", "person")

            # Prevent accidental company flag for people
            if vals.get("company_type") == "company" and (vals.get("is_contact") or vals.get("is_patient")):
                _logger.warning("Forcing company_type='person' to prevent implicit is_company=True")
                vals["company_type"] = "person"

            # Ensure we keep 'New' until save
            if "customer_code" not in vals or vals["customer_code"] in PLACEHOLDERS:
                vals["customer_code"] = _("New")

        partners = super().create(vals_list)

        # Accounts → ID#### (use your sequence)
        accounts = partners.filtered(lambda p: p.is_account and (p.customer_code in PLACEHOLDERS))
        if accounts:
            for p in accounts:
                seq_raw = self.env["ir.sequence"].next_by_code("res.partner.account") or "0"
                code = f"ID{seq_raw.zfill(4)}"
                p.with_context(_skip_customer_code_sync=True).write({"customer_code": code})

            # Important: affiliates created on the same form *before* the account was saved
            # still have placeholders; now that the parent has a real code, number them.
            for acc in accounts:
                acc.affiliate_ids.filtered(lambda a: a.customer_code in PLACEHOLDERS)._assign_affiliate_codes_batch()

        # Contacts / Patients (global sequences – no collision in batch)
        contacts = partners.filtered(lambda p: p.is_contact and not p.is_patient and (p.customer_code in PLACEHOLDERS))
        if contacts:
            for p in contacts:
                p.with_context(_skip_customer_code_sync=True).write({
                    "customer_code": self.env["ir.sequence"].next_by_code("res.partner.contact")
                })

        patients = partners.filtered(lambda p: p.is_patient and (p.customer_code in PLACEHOLDERS))
        if patients:
            for p in patients:
                p.with_context(_skip_customer_code_sync=True).write({
                    "customer_code": self.env["ir.sequence"].next_by_code("res.partner.patient")
                })

        # Affiliates created standalone (or on forms where parent already had a code)
        partners._assign_affiliate_codes_batch()

        # Post-create side-effects you already had
        for partner, vals in zip(partners, vals_list):
            if partner.use_parent_invoice_address or partner.use_parent_shipping_address:
                partner._onchange_parent_address_flags()
            if self.get_fields_contact_points().intersection(vals.keys()) and not self._context.get("compute_contact_points"):
                partner.with_context(compute_contact_points=True)._compute_contact_points()

        return partners


    def write(self, vals):
        """
        - Keep your validations, role protections, parent reassignment guard, etc.
        - If a record still has a placeholder ('New', '/', '', False) after write and
        it now has a clear role/parent, assign a real code (once).
        - When parent changes on an existing record, regenerate code per your rule.
        - Batch-assign affiliate suffixes safely.
        """
        PLACEHOLDERS = {False, "", "/", _("New")}

        if vals.get("is_company") is True:
            _logger.warning(
                "[TRACE] write() received is_company=True on partner ID(s): %s\nVALS: %s",
                self.ids, vals
            )

        _logger.info("[WRITE] Updating partner(s) with values: %s", vals)

        # Safety / role conflict cleanup
        if vals.get("is_patient"):
            vals.pop("is_contact", None)
        if vals.get("is_contact") and vals.get("is_company"):
            raise ValidationError("A contact cannot be marked as a company.")
        if "is_company" in vals:
            for partner in self:
                if (partner.is_contact or vals.get("is_contact")) and vals["is_company"]:
                    raise ValidationError("Contacts cannot be marked as companies.")

        # Prevent archiving linked users
        if vals.get("active") is False and not self._context.get("from_create_profile"):
            self.invalidate_recordset(["user_ids"])
            users = self.env["res.users"].sudo().search([("partner_id", "in", self.ids)])
            if users:
                if self.env["res.users"].sudo(False).check_access_rights("write", raise_exception=False):
                    raise RedirectWarning(
                        _("You cannot archive contacts linked to an active user.\n"
                        "You first need to archive their associated user.\n\n"
                        "Linked active users : %(names)s",
                        names=", ".join(u.display_name for u in users)),
                        users._action_show(), _("Go to users"),
                    )
                else:
                    raise ValidationError(_(
                        "You cannot archive contacts linked to an active user.\n"
                        "Ask an administrator to archive their associated user first.\n\n"
                        "Linked active users :\n%(names)s",
                        names=", ".join(u.display_name for u in users)
                    ))

        # Parent reassignment & circular checks + code regeneration on true parent switch
        if "parent_id" in vals:
            new_parent = self.env["res.partner"].browse(vals["parent_id"])
            for partner in self:
                if partner.id == new_parent.id:
                    raise ValidationError("A partner cannot be its own parent.")
                if partner._is_circular_reference(new_parent):
                    raise ValidationError("Circular reference detected in the hierarchy.")
                if partner.parent_id and partner.parent_id != new_parent:
                    # regenerate this partner's code on true parent move
                    if partner.customer_code in PLACEHOLDERS or partner.is_affiliate:
                        new_code = partner._generate_customer_code({
                            "parent_id": new_parent.id,
                            "is_account": partner.is_account,
                            "is_affiliate": partner.is_affiliate,
                            "is_contact": partner.is_contact,
                            "is_patient": partner.is_patient,
                        })
                        if new_code:
                            partner.with_context(_skip_customer_code_sync=True).write({"customer_code": new_code})
                    partner._update_child_codes()

        if vals.get("website"):
            vals["website"] = self._clean_website(vals["website"])
        if vals.get("parent_id"):
            vals["company_name"] = False

        # Company sync
        if "company_id" in vals:
            company_id = vals["company_id"]
            for partner in self:
                if company_id and partner.user_ids:
                    company = self.env["res.company"].browse(company_id)
                    user_companies = {user.company_id for user in partner.user_ids}
                    if len(user_companies) > 1 or company not in user_companies:
                        raise UserError("The selected company is not compatible with the companies of the related user(s).")
                if partner.child_ids:
                    partner.child_ids.write({"company_id": company_id})

        # Execute write (preserve your sudo/is_company tweak)
        result = True
        if "is_company" in vals and self.user_has_groups("base.group_partner_manager") and not self.env.su:
            is_company = vals.pop("is_company")
            result = super(Partner, self.sudo()).write({"is_company": is_company})
        if not self._context.get("from_create_profile"):
            result = result and super().write(vals)

        # Post-write syncing
        for partner in self:
            if any(u._is_internal() for u in partner.user_ids if u != self.env.user):
                self.env["res.users"].check_access_rights("write")
            partner._fields_sync(vals)

        if {"use_parent_invoice_address", "use_parent_shipping_address", "parent_id"} & set(vals):
            self._onchange_parent_address_flags()

        self._validate_affiliate_parent()
        self._update_children(vals)

        if self.get_fields_contact_points().intersection(vals.keys()) and not self._context.get("compute_contact_points"):
            for partner in self:
                partner.with_context(compute_contact_points=True)._compute_contact_points()

        # Assign real codes to any placeholders that slipped through (non-affiliates)
        still_placeholder = self.filtered(lambda p: (p.customer_code in PLACEHOLDERS) and (p.is_account or p.is_contact or p.is_patient) and not p.is_affiliate)
        for p in still_placeholder:
            real_code = p._generate_customer_code({
                "parent_id": p.parent_id.id,
                "is_account": p.is_account,
                "is_affiliate": p.is_affiliate,
                "is_contact": p.is_contact,
                "is_patient": p.is_patient,
            })
            if real_code:
                p.with_context(_skip_customer_code_sync=True).write({"customer_code": real_code})
                _logger.info("[WRITE] Assigned customer_code for %s -> %s", p.display_name, real_code)

        # Finally, (re)number affiliates with placeholders in batch (safe with FOR UPDATE)
        self._assign_affiliate_codes_batch()

        _logger.info("[WRITE] Partner(s) updated successfully.")
        return result

    def copy(self, default=None):
        """When duplicating, keep the placeholder so the duplicate gets a fresh code on save."""
        default = dict(default or {})
        default.setdefault("customer_code", _("New"))
        return super().copy(default)


    @api.model
    def _commercial_fields(self):
        """Add company_ids to the commercial fields that will be synced with
         childs. Ideal would be that this field is isolated from company field,
         but it involves a lot of development (default value, incoherences
         parent/child...).
        :return: List of field names to be synced.
        """
        commercial_fields = super()._commercial_fields()
        commercial_fields += ["company_ids"]
        return commercial_fields

    @api.depends("is_commercial_partner", "parent_id")
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_commercial_partner or not partner.parent_id:
                partner.commercial_partner_id = partner
            elif partner.parent_id.id == partner.id:  # Prevent recursion
                partner.commercial_partner_id = partner
            else:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id

    def _commercial_sync_to_children(self, visited=None):
        """Recursively sync commercial fields to all non-company child contacts."""

        visited = visited or set()

        # Prevent infinite recursion
        if self.id in visited:
            return False

        visited.add(self.id)

        # Get commercial field values from the current commercial partner
        commercial_vals = self.commercial_partner_id._update_fields_values(self._commercial_fields())

        # Filter children that should inherit commercial values
        children_to_sync = self.child_ids.filtered(lambda child: not child.is_company)

        # Apply values and recurse
        for child in children_to_sync:
            child.write(commercial_vals)
            child._compute_commercial_partner()
            child._commercial_sync_to_children(visited=visited)

        return True

    @api.model
    def _amend_company_id(self, vals):
        if "company_ids" in vals:
            if not vals["company_ids"]:
                vals["company_id"] = False
            else:
                for item in vals["company_ids"]:
                    if item[0] in (Command.UPDATE, Command.LINK):
                        vals["company_id"] = item[1]
                    elif item[0] in (Command.DELETE, Command.UNLINK, Command.CLEAR):
                        vals["company_id"] = False
                    elif item[0] == Command.SET:
                        if item[2]:
                            vals["company_id"] = item[2][0]
                        else:  # pragma: no cover
                            vals["company_id"] = False
        elif "company_id" not in vals:
            vals["company_ids"] = False
        return vals

    @api.constrains("company_ids")
    def _check_company_id(self):
        for rec in self:
            if rec.user_ids:
                user_company_ids = set(rec.user_ids.mapped("company_ids").ids)
                partner_company_ids = set(rec.company_ids.ids)

                if (
                    not user_company_ids.issubset(partner_company_ids)
                    and partner_company_ids
                ):
                    raise ValidationError(
                        _(
                            "The partner must have at least all the companies "
                            "associated with the user."
                        )
                    )

    def _inverse_company_id(self):
        if self.env.context.get("from_res_users"):
            # don't delete all partner company_ids when
            # the user's related company_id is modified.
            for record in self:
                company = record.company_id
                if company:
                    record.company_ids = [Command.link(company.id)]
            return
        else:
            return super()._inverse_company_id()



    def _update_related_records(self):
        """Update contacts, patients, and orders when the parent changes."""
        for record in self.child_ids | self.patient_ids:
            _logger.info(f"Updating {record.name}'s parent to {self.parent_id.name}")
            record.parent_id = self.parent_id

    def _generate_customer_code(self, vals):
        """Generate a customer_code for Accounts, Affiliates, Patients, Contacts, or fallback."""

        def next_seq(code):
            return self.env["ir.sequence"].next_by_code(code)

        # Normalize booleans for safety (e.g., False if unset)
        is_account = bool(vals.get("is_account"))
        is_affiliate = bool(vals.get("is_affiliate"))
        is_contact = bool(vals.get("is_contact"))
        is_patient = bool(vals.get("is_patient"))
        parent_id = vals.get("parent_id")
        parent = self.env["res.partner"].browse(parent_id) if parent_id else None

        # ░ Safeguard: prevent misassigned `is_contact`
        if is_account or is_affiliate:
            vals["is_contact"] = False

        # 🔹 Accounts: global sequential ID
        if is_account:
            return f"ID{next_seq('res.partner.account').zfill(4)}"

        # 🔹 Affiliates: scoped under parent.account
        if is_affiliate and parent and parent.customer_code:
            last_affiliate = self.env["res.partner"].search(
                [
                    ("parent_id", "=", parent.id),
                    ("is_affiliate", "=", True),
                    ("customer_code", "!=", False),
                ],
                order="customer_code DESC",
                limit=1,
            )

            if last_affiliate:
                last_number = last_affiliate.customer_code.split("-")[-1]
                next_number = f"{int(last_number) + 1:02d}" if last_number.isdigit() else "01"
            else:
                next_number = "01"

            # 🔹 Limit affiliate nesting to max 2 levels
            code_parts = parent.customer_code.split("-")
            base_code = "-".join(code_parts[:2]) if len(code_parts) > 2 else parent.customer_code
            return f"{base_code}-{next_number}"

        # 🔹 Patients
        if is_patient:
            return next_seq("res.partner.patient")

        # 🔹 Contacts
        if is_contact:
            return next_seq("res.partner.contact")

        # 🔹 Fallbacks
        if parent and parent.customer_code:
            _logger.warning("Unclassified child record defaulting to contact sequence")
            return next_seq("res.partner.contact")

        _logger.warning("Generating generic code due to missing flags: %s", vals)
        return next_seq("res.partner.generic")

    def _update_child_codes(self):
        """Recursively update customer codes for children when a parent changes."""
        for child in self.child_ids:
            old_code = child.customer_code
            child.customer_code = self._generate_customer_code(
                {"parent_id": self.id, "is_contact": True}
            )
            _logger.info(
                "Updated child customer_code from %s to %s",
                old_code,
                child.customer_code,
            )
            child._update_child_codes()

    def _is_circular_reference(self, new_parent):
        """Check if assigning new parent creates a circular reference."""
        visited = set()
        while new_parent:
            if new_parent.id in visited:
                return True
            visited.add(new_parent.id)
            new_parent = new_parent.parent_id
        return False

    def merge_affiliates(self, target_affiliate):
        """Merge the current affiliate into another, moving contacts and patients."""
        self.ensure_one()

        if not self.is_affiliate or not target_affiliate.is_affiliate:
            raise ValidationError("Both partners must be affiliates to merge.")

        if self.id == target_affiliate.id:
            raise ValidationError("Cannot merge an affiliate with itself.")

        if self._is_circular_reference(target_affiliate):
            raise ValidationError("Merging would create a circular hierarchy.")

        try:
            _logger.info(
                "Merging affiliate %s into %s", self.name, target_affiliate.name
            )

            # Move related contacts & patients
            self.child_ids.write({"parent_id": target_affiliate.id})
            self.patient_ids.write({"parent_id": target_affiliate.id})

            # Archive old affiliate instead of deleting
            self.write(
                {
                    "is_merged": True,
                    "merged_into_id": target_affiliate.id,
                    "active": False,
                }
            )

            _logger.info(
                "Successfully merged %s into %s", self.name, target_affiliate.name
            )

        except Exception as e:
            _logger.error("Failed to merge affiliates: %s", str(e))
            raise ValidationError("An error occurred while merging affiliates.")

    def view_affiliates(self):
        return {
            "name": _("Affiliates"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "tree,form",
            "view_id": False,
            "domain": [("parent_id", "in", self.ids), ("is_affiliate", "=", True)],
            "target": "current",
        }

    def action_open_affiliate_selection(self):
        """Opens a window to select an Affiliate for this Partner."""
        return {
            "type": "ir.actions.act_window",
            "name": "Select Affiliate",
            "res_model": "res.partner",
            "view_mode": "tree,form",
            "target": "new",
            "domain": [("is_affiliate", "=", True), ("parent_id", "=", self.id)],
            "context": {"default_parent_id": self.id},
        }

    def _update_fields_view_get_result(self, result, view_type="form"):
        if view_type == "form" and not self._context.get("display_original_view"):
            doc = etree.XML(result["arch"])
            for node in doc.xpath("//field[@name='child_ids']"):
                node.set(
                    "modifiers",
                    json.dumps(
                        {
                            "default_is_account": False,
                            "default_is_affiliate": False,
                            "default_is_contact": False,
                            "default_is_patient": False,
                        }
                    ),
                )
            result["arch"] = etree.tostring(doc)
        return result

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super(Partner, self).get_view(view_id, view_type, **options)

        # Modify the view XML
        doc = etree.XML(result["arch"])
        for node in doc.xpath("//field[@name='child_ids']"):
            node.set(
                "domain",
                "[('is_contact', '=', True), ('is_patient', '=', False), ('is_company', '=', False)]",
            )

        result["arch"] = etree.tostring(doc)

        # Update metadata if necessary
        node = etree.fromstring(result["arch"])
        view_fields = set(
            el.get("name") for el in node.xpath(".//field[not(ancestor::field)]")
        )
        result["fields"] = self.fields_get(view_fields)

        return self._update_fields_view_get_result(result, view_type)

    @api.depends(
        "complete_name",
        "email",
        "vat",
        "state_id",
        "country_id",
        "commercial_company_name",
    )
    @api.depends_context(
        "show_address", "partner_show_db_id", "address_inline", "show_email", "show_vat"
    )
    def _compute_display_name(self):
        for partner in self:
            # Check if we're in the context of selecting a primary_contact_id
            if self._context.get("primary_contact_selection"):
                # Display only the contact's name if it's a contact
                partner.display_name = partner.name
            else:
                # Default Odoo behavior
                name = partner.complete_name
                if partner._context.get("show_address"):
                    name = name + "\n" + partner._display_address(without_company=True)
                name = name.strip()
                if partner._context.get("partner_show_db_id"):
                    name = f"{name} ({partner.id})"
                if partner._context.get("address_inline"):
                    name = ", ".join(filter(None, name.split("\n")))
                if partner._context.get("show_email") and partner.email:
                    name = f"{name} <{partner.email}>"
                if partner._context.get("show_vat") and partner.vat:
                    name = f"{name} ‒ {partner.vat}"
                partner.display_name = name

    @api.model
    def _format_args(self, args):
        for cond in args or []:
            if (
                len(cond) == 3
                and cond[2]
                and isinstance(cond[2], list)
                and isinstance(cond[2][0], list)
            ):
                for index, item in enumerate(cond[2]):
                    if item[0] == 1:
                        cond[2][index] = item[1]
                    elif item[0] == 6:
                        cond[2] = item[2]
                        break

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if not args:
            args = [("id", "!=", 0)]

        domain = [
            "|",
            ("name", operator, name),
            "|",
            ("customer_code", operator, name),
            ("legacy_customer_code", operator, name),
        ]
        return self.search(domain + args, limit=limit).name_get()

    def _search(self, args, offset=0, limit=None, order=None, count=False):
        self._format_args(args)
        if count:
            return super(Partner, self)._search(
                args, offset=offset, limit=limit, order=order, count=True
            )
        return super(Partner, self)._search(
            args, offset=offset, limit=limit, order=order
        )

    # Partner Flags
    partner_flag_ids = fields.One2many("res.partner.flag", inverse_name="partner_id")
    partner_flag_count = fields.Integer(compute="_compute_partner_flag_count")

    @api.depends("partner_flag_ids")
    def _compute_partner_flag_count(self):
        for rec in self:
            rec.partner_flag_count = len(rec.partner_flag_ids.ids)

    def action_view_partner_flags(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "nwpl_odoo_master.partner_flag_action"
        )
        result["context"] = {"default_partner_id": self.id}
        result["domain"] = "[('partner_id', '=', " + str(self.id) + ")]"
        if len(self.partner_flag_ids) == 1:
            res = self.env.ref("partner.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.partner_flag_ids.id
        return result

    # Portal Users
    create_users_button = fields.Boolean(
        compute="_compute_create_users_button",
        store=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        index=True,
        tracking=True,
        help="Link to the partner record.",
    )

    related_user_id = fields.Many2one(
        related="partner_id.user_id",
        string="Related User",
        readonly=True,
    )
    
    x_signature_template_id = fields.Many2one(
        'sign.template',
        string='Signature Agreement',
        tracking=True
    )

    has_portal_access = fields.Boolean(
        string='Has Portal Access',
        compute='_compute_has_portal_access',
    )
    
    activation_link = fields.Char(
        string='Portal Activation Link',
        compute='_compute_activation_link',
    )
    
    @api.depends('user_ids', 'user_ids.active')
    def _compute_has_portal_access(self):
        for partner in self:
            # Check if partner has portal user
            portal_user = self.env['res.users'].sudo().search_count([
                ('partner_id', '=', partner.id),
                ('active', '=', True)
            ])
            if portal_user > 0:
                partner.has_portal_access = True
            else:
                partner.has_portal_access = False
            _logger.info('Computing portal access for partner %s (ID: %s): %s', 
                        partner.name, partner.id, partner.has_portal_access)

    @api.depends('has_portal_access')
    def _compute_activation_link(self):
        for partner in self:
            if partner.has_portal_access:
                signup_url = partner.with_context(signup_force_type_in_url='signup')._get_signup_url_for_action()
                partner.activation_link = signup_url.get(partner.id, '')
            else:
                partner.activation_link = False

    def toggle_portal_access(self):
        self.ensure_one()
        
        _logger.info(
            'Toggling portal access for partner %s (ID: %s). Current status: %s', 
            self.name, self.id, self.has_portal_access
        )

        if not self.email:
            raise ValidationError('Please add an email address before granting portal access.')

        if not self.name:
            raise ValidationError('Contact must have a name before granting portal access.')

        Users = self.env['res.users'].sudo()
        portal_group = self.env.ref("base.group_portal")

        if self.has_portal_access:
            portal_user = Users.search([('partner_id', '=', self.id), ('active', '=', True)], limit=1)
            if portal_user:
                _logger.info('Deactivating portal user: %s', portal_user.id)
                portal_user.write({'active': False})
                portal_user.groups_id -= portal_group
        else:
            portal_user = Users.search([('partner_id', '=', self.id)], limit=1)
            if not portal_user:
                _logger.info('Creating new portal user for %s', self.email)
                portal_user = Users.create({
                    'name': self.name,
                    'login': self.email,
                    'email': self.email,
                    'partner_id': self.id,
                    'groups_id': [(6, 0, [portal_group.id])]
                })
            else:
                _logger.info('Reactivating existing portal user %s', portal_user.id)
                portal_user.write({'active': True})
                portal_user.groups_id |= portal_group

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            }

    def action_send_agreement(self):
        if self.x_signature_template_id and self.email:
            template = self.x_signature_template_id

            # Get roles from template's signature items
            roles = template.sign_item_ids.mapped('responsible_id')
            if not roles:
                raise ValidationError('The selected template has no signature roles defined. Please configure the template first.')

            # Create signature request
            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'subject': f'Signature Request: {template.name}',
                'reference': template.name,
                'request_item_ids': [(0, 0, {
                    'role_id': role.id,
                    'partner_id': self.id,
                }) for role in roles],
            })

            # Reset the template field after sending
            self.x_signature_template_id = False

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Signature request sent to {self.email}',
                    'type': 'success',
                    'sticky': False,
                }
            }
        elif not self.email:
            raise ValidationError('Please add an email address before requesting signature.')
        elif not self.x_signature_template_id:
            raise ValidationError('Please select a signature template before requesting signature.')

    @api.depends("partner_id.user_ids")
    def _compute_create_users_button(self):
        """Compute the visibility of the 'Create Portal User' button."""
        for record in self:
            record.create_users_button = not bool(record.partner_id.user_ids)

    def create_portal_user(self):
        """Create a portal user for the partner if one does not already exist."""
        self.ensure_one()
        if self.user_ids:
            raise UserError(_("A user for this partner already exists."))

        portal_group = self.env.ref("base.group_portal")

        user = self.env['res.users'].sudo().create({
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'partner_id': self.id,
            'groups_id': [(6, 0, [portal_group.id])]
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Portal User Created',
                'message': f'Portal user {user.name} has been created.',
                'type': 'success',
                'sticky': False,
            }
        }

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

    def open_partner_form(self):
        """Open contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

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

    # Roles
    is_role_required = fields.Boolean(
        compute="_compute_is_role_required",
        inverse="_inverse_is_role_required",
        string="Is Role Required",
        store=False,
    )
    
    @api.depends("is_contact", "is_patient", "contact_role_ids")
    def _compute_is_role_required(self):
        for record in self:
            record.is_role_required = (
                record.is_contact
                and not record.is_patient
                and not record.contact_role_ids
            )

    def _inverse_is_role_required(self):
        # no raise here; constraint already enforces it
        return

    @api.constrains("is_contact", "is_patient", "contact_role_ids")
    def _check_contact_roles(self):
        for record in self:
            if record.is_contact and not record.is_patient and not record.contact_role_ids:
                raise ValidationError(_("Roles are required for contacts."))

    # Sales Orders
    # Raw link
    sale_order_ids = fields.One2many(
        "sale.order", "partner_id", string="Sale Orders"
    )

    # Buckets
    current_sale_order_ids = fields.One2many(
        "sale.order", compute="_compute_current_sale_order_ids", string="Current Orders", store=False
    )
    completed_sale_order_ids = fields.One2many(
        "sale.order", compute="_compute_completed_sale_order_ids", string="Completed Orders", store=False
    )
    canceled_sale_order_ids = fields.One2many(
        "sale.order", compute="_compute_canceled_sale_order_ids", string="Canceled Quotes/Orders", store=False
    )
    historic_sale_order_ids = fields.One2many(
        "sale.order", compute="_compute_historic_sale_order_ids", string="Historic Orders (Re-orderable)", store=False
    )

    reorder_count = fields.Integer(compute="_compute_reorder_order_count", string="Reorder")

    def _compute_current_sale_order_ids(self):
        for partner in self:
            partner.current_sale_order_ids = partner.sale_order_ids.filtered(
                lambda so: so.state not in ("done", "cancel")
            )

    def _compute_completed_sale_order_ids(self):
        for partner in self:
            partner.completed_sale_order_ids = partner.sale_order_ids.filtered(
                lambda so: so.state == "done"
            )

    def _compute_canceled_sale_order_ids(self):
        for partner in self:
            partner.canceled_sale_order_ids = partner.sale_order_ids.filtered(
                lambda so: so.state == "cancel"
            )

    def _compute_historic_sale_order_ids(self):
        """Historic & re-orderable (your original intent)."""
        for partner in self:
            partner.historic_sale_order_ids = partner.sale_order_ids.filtered(
                lambda so: so.state in ("done", "cancel") and so.is_reorder
            )

    def _compute_reorder_order_count(self):
        for partner in self:
            partner.reorder_count = len(partner.historic_sale_order_ids)

    def open_sale_from_view_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [
            ("partner_id", "=", self.id),
            ("state", "=", "sale"),
            ("is_reorder", "=", True),
        ]
        return action
