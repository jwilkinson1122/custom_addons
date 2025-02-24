import logging
import base64
import json
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import _, models, fields, tools, api, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval
from .res_partner_contact_point_mixin import CONTACT_POINT_TYPES

_logger = logging.getLogger(__name__)


INVOICE = "invoice"


class Partner(models.Model):
    _inherit = ["res.partner", "incrementing.sequence.mixin"]
    _name = "res.partner"
    _sequence_group = "parent_id"
    # _inherit = "res.partner"

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

    # contact_point_ids = fields.One2many(
    #     "res.partner.contact_point", "partner_id", "Contact Points"
    # )
    # email = fields.Char(
    #     compute="_compute_contact_points", inverse="_set_email", store=True
    # )
    # phone = fields.Char(
    #     compute="_compute_contact_points", inverse="_set_phone", store=True
    # )
    # mobile = fields.Char(
    #     compute="_compute_contact_points", inverse="_set_mobile", store=True
    # )
    # fax_number = fields.Char(string="Fax")

    ref = fields.Char(string="Ref", index=True)
    customer_code = fields.Char(
        string="Customer Code", readonly=True, default=lambda self: _("New")
    )
    legacy_customer_code = fields.Char("Legacy ID", readonly=True)

    partner_company_type = fields.Many2one(
        comodel_name="partner.company.type",
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

    group_id = fields.Many2one("res.partner.groups", string="Group")

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

    # type = fields.Selection(
    #     selection_add=[
    #         ("account", "Account Address"),
    #         ("affiliate", "Affiliate Address"),
    #         ("supplier", "Supplier Address"),
    #         ("patient", "Patient Address"),
    #         ("other",),
    #     ],
    #     string="Address Type",
    #     store=True,
    #     default=False,
    # )

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

    # parent_id = fields.Many2one('res.partner', string='Related Company', index=True)

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

    child_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="parent_id",
        domain=[("active", "=", True), ("is_company", "=", False)],
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

    contact_role_ids = fields.Many2many(string="Roles", comodel_name="contact.role")

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

    @api.depends("contact_point_ids.name", "contact_point_ids.is_default")
    def _compute_contact_points(self):
        for partner in self:
            for cptype, label in CONTACT_POINT_TYPES:
                partner[cptype] = partner.contact_point_ids.filtered(
                    lambda cp: cp.contact_point_type == cptype and cp.is_default
                ).name

    def _set_contact_point(self, contact_point_type):
        if self[contact_point_type]:
            contact_point = self.contact_point_ids.filtered(
                lambda cp: cp.name == self[contact_point_type]
                and cp.contact_point_type == contact_point_type
            )
            if not contact_point:
                self.contact_point_ids.create(
                    {
                        "name": self[contact_point_type],
                        "partner_id": self.id,
                        "contact_point_type": contact_point_type,
                        "is_default": True,
                    }
                )
            elif not contact_point.is_default:
                contact_point.is_default = True

    def get_fields_contact_points(self):
        return {"phone", "mobile", "email"}

    patient_id = fields.Many2one(
        "res.partner",
        string="Related Contact",
        domain=[("is_patient", "=", True)],
        help="Link to the related patient.",
    )

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
    patient_text = fields.Char(compute="_compute_patient_text")

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

    # Contacts
    @api.depends("child_ids")
    def _compute_contacts_count(self):
        self._compute_count(
            "child_ids",
            "contacts_count",
            filters=lambda r: r.is_contact and not r.is_company and not r.is_patient,
        )

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
                        lambda r: r.is_contact and not r.is_company and not r.is_patient
                    )
                    get_indirect_contacts(affiliate)

            get_indirect_contacts(partner)
            partner.sub_contact_ids = all_sub_contacts

    # Patients
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

    # Billing Address Fields
    # billing_street = fields.Char("Billing Street")
    # billing_street2 = fields.Char("Billing Street 2")
    # billing_city = fields.Char("Billing City")
    # billing_state_id = fields.Many2one("res.country.state", "Billing State")
    # billing_zip = fields.Char("Billing ZIP")
    # billing_country_id = fields.Many2one("res.country", "Billing Country")

    # Shipping Address Fields
    # shipping_street = fields.Char("Shipping Street")
    # shipping_street2 = fields.Char("Shipping Street 2")
    # shipping_city = fields.Char("Shipping City")
    # shipping_state_id = fields.Many2one("res.country.state", "Shipping State")
    # shipping_zip = fields.Char("Shipping ZIP")
    # shipping_country_id = fields.Many2one("res.country", "Shipping Country")

    # Boolean Field to Copy Billing Address to Shipping
    # same_as_billing = fields.Boolean("Same As Billing Address?", default=False)

    # Onchange Methods
    # @api.onchange("same_as_billing")
    # def _onchange_same_as_billing(self):
    #     if self.same_as_billing:
    #         self.shipping_street = self.billing_street
    #         self.shipping_street2 = self.billing_street2
    #         self.shipping_city = self.billing_city
    #         self.shipping_state_id = self.billing_state_id
    #         self.shipping_zip = self.billing_zip
    #         self.shipping_country_id = self.billing_country_id

    # Onchange Methods
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
        if self.partner_type_id:
            self.update(self._get_inherit_values(self.partner_type_id))
            if self.partner_type_id.type == "contact":
                self.is_contact = True
                self.type = False
            else:
                self.is_contact = False
                self.type = (
                    self.partner_type_id.type
                    if self.partner_type_id.type
                    in dict(self._fields["type"].selection).keys()
                    else False
                )

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """Handles changes in parent_id:
        - Updates customer_code if parent changes.
        - Stores previous parent_id for tracking.
        - Filters primary_contact_id to only show contacts of the selected parent.
        """

        self.apply_contact_logic()

        # ✅ Update domain for primary_contact_id
        domain = [("is_contact", "=", True), ("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))

            # ✅ Update customer_code safely when parent changes
            if self.previous_parent_id and self.previous_parent_id != self.parent_id:
                _logger.info(
                    f"Reassigning parent for {self.name} from {self.previous_parent_id.name} to {self.parent_id.name}"
                )

                # Store previous code before updating
                if self.customer_code and self.customer_code != _("New"):
                    self.legacy_customer_code = self.customer_code

                self.customer_code = self._generate_customer_code()
                self._update_related_records()

            # ✅ Store the new parent as previous_parent_id
            self.previous_parent_id = self.parent_id

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
    @api.onchange(
        "parent_id", "use_parent_invoice_address", "use_parent_shipping_address"
    )
    def _onchange_parent_address_flags(self):
        _logger.debug(
            f"Triggered onchange for parent_id: {self.parent_id}, use_parent_invoice_address: {self.use_parent_invoice_address}, use_parent_shipping_address: {self.use_parent_shipping_address}"
        )

        if self.use_parent_invoice_address and self.parent_id:
            self._apply_parent_address(address_type="invoice")
        if self.use_parent_shipping_address and self.parent_id:
            self._apply_parent_address(address_type="shipping")

    def _apply_parent_address(self, address_type):
        address_fields = ["street", "street2", "city", "zip", "state_id", "country_id"]
        parent = self.parent_id

        if address_type == "invoice":
            _logger.debug(f"Applying parent invoice address from: {parent.name}")
        elif address_type == "shipping":
            _logger.debug(f"Applying parent shipping address from: {parent.name}")

        for field in address_fields:
            parent_value = getattr(parent, field, False)
            if field in ["state_id", "country_id"]:
                parent_value = parent_value.id if parent_value else False
            self[field] = parent_value

    @api.model
    def create(self, vals):
        """Create a partner with validations, rollback safety, and address handling."""
        _logger.debug("Received vals for create: %s", vals)

        # Ensure `is_contact` is NOT set when creating an Account or Affiliate
        if vals.get("is_account") or vals.get("is_affiliate"):
            vals["is_contact"] = False  # Prevent incorrect `is_contact=True`

        if vals.get("parent_id"):
            vals["parent_id"] = int(vals["parent_id"])

        with self.env.cr.savepoint():  # Ensures rollback if any error occurs
            if vals.get("customer_code", _("New")) == _("New"):
                vals["customer_code"] = self._generate_customer_code(vals)
                _logger.debug("Generated customer_code: %s", vals["customer_code"])

            partner = super().create(vals)

            # Handle address inheritance
            if (
                partner.use_parent_invoice_address
                or partner.use_parent_shipping_address
            ):
                partner._onchange_parent_address_flags()

            # Force recompute contact points for phone, mobile, and email
            if self.get_fields_contact_points().intersection(
                vals.keys()
            ) and not self._context.get("compute_contact_points"):
                partner.with_context(
                    compute_contact_points=True
                )._compute_contact_points()

        return partner

    def write(self, vals):
        """Update partner and apply relevant changes, including address inheritance and customer code generation."""
        _logger.info("Updating partner(s) with values: %s", vals)

        if "parent_id" in vals:
            new_parent = self.env["res.partner"].browse(vals["parent_id"])
            for partner in self:
                if new_parent and partner.id == new_parent.id:
                    raise ValidationError("A partner cannot be its own parent.")

                if partner._is_circular_reference(new_parent):
                    raise ValidationError(
                        "Circular reference detected in the hierarchy."
                    )

                vals["customer_code"] = self._generate_customer_code(vals)
                partner._update_child_codes()

        result = super().write(vals)

        # Apply address inheritance logic if necessary
        if (
            "use_parent_invoice_address" in vals
            or "use_parent_shipping_address" in vals
            or "parent_id" in vals
        ):
            self._onchange_parent_address_flags()

        self._validate_affiliate_parent()
        self._update_children(vals)

        # Force recompute contact points when relevant fields change
        if self.get_fields_contact_points().intersection(
            vals.keys()
        ) and not self._context.get("compute_contact_points"):
            for partner in self:
                partner.with_context(
                    compute_contact_points=True
                )._compute_contact_points()

        _logger.info("Partner(s) updated successfully.")
        return result

    def _set_email(self):
        self._set_contact_point("email")

    def _set_phone(self):
        self._set_contact_point("phone")

    def _set_mobile(self):
        self._set_contact_point("mobile")

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

    def _update_related_records(self):
        """Update contacts, patients, and orders when the parent changes."""
        for record in self.child_ids | self.patient_ids:
            _logger.info(f"Updating {record.name}'s parent to {self.parent_id.name}")
            record.parent_id = self.parent_id

    def _generate_customer_code(self, vals):
        """Generate customer codes ensuring that each Account's Affiliates increment independently."""

        sequence_map = {
            "is_account": "res.partner.account",
            "is_affiliate": "res.partner.affiliate",
            "is_contact": "res.partner.contact",
            "is_patient": "res.partner.patient",
        }

        # ✅ Ensure `is_contact` is NOT set when creating an Account or Affiliate
        if vals.get("is_account") or vals.get("is_affiliate"):
            vals["is_contact"] = False  # ❌ Prevent accidental setting of is_contact

        # ✅ Accounts get a unique sequence (ID0001, ID0002, etc.)
        if vals.get("is_account"):
            return f"ID{self.env['ir.sequence'].next_by_code('res.partner.account').zfill(4)}"

        parent = (
            self.env["res.partner"].browse(vals.get("parent_id"))
            if vals.get("parent_id")
            else None
        )

        # ✅ Ensure Affiliates increment within the Account, not across all Affiliates globally
        if vals.get("is_affiliate") and parent and parent.customer_code:
            # 🔹 Find the last used affiliate number **for this specific Account**
            existing_affiliates = self.env["res.partner"].search(
                [
                    ("parent_id", "=", parent.id),
                    ("is_affiliate", "=", True),
                    ("customer_code", "!=", False),
                ],
                order="customer_code DESC",
                limit=1,
            )

            # Extract the last affiliate's number and increment it
            if existing_affiliates:
                last_code_parts = existing_affiliates.customer_code.split("-")
                last_number = (
                    int(last_code_parts[-1]) if last_code_parts[-1].isdigit() else 0
                )
                new_number = f"{last_number + 1:02d}"  # Use 2-digit format (01, 02, 03)
            else:
                new_number = "01"  # Start fresh if no Affiliates exist yet

            # 🔹 **Limit Nesting Depth** (Prevent long codes like ID0001-001-001-001)
            max_depth = 2  # Limit depth to 2 levels (e.g., ID0001-01, ID0001-01-01)
            code_parts = parent.customer_code.split("-")

            if len(code_parts) >= max_depth + 1:
                base_code = "-".join(code_parts[:max_depth])
            else:
                base_code = parent.customer_code

            return f"{base_code}-{new_number}"

        # ✅ Ensure contacts & patients always get a unique sequence
        for key, seq_code in sequence_map.items():
            if vals.get(key):
                return self.env["ir.sequence"].next_by_code(seq_code)

        return self.env["ir.sequence"].next_by_code("res.partner.generic")

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

        domain = ["|", ("name", operator, name), ("customer_code", operator, name)]
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
        """
        Ensure that roles are set as required when applicable.
        """
        for record in self:
            _logger.debug(
                f"Processing _inverse_is_role_required for record ID {record.id}:"
            )
            _logger.debug(
                f"Current is_role_required: {record.is_role_required}, Contact roles: {record.contact_role_ids}"
            )
            if record.is_role_required and not record.contact_role_ids:
                _logger.error("ValidationError: Roles are required for contacts.")
                raise ValidationError("Roles are required for contacts.")

    @api.constrains("is_contact", "contact_role_ids")
    def _check_contact_roles(self):
        for record in self:
            if (
                record.is_contact
                and not record.is_patient
                and not record.contact_role_ids
            ):
                raise ValidationError(_("Roles are required for contacts."))

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
        """Handle sync of commercial fields to descendants"""
        if visited is None:
            visited = set()
        if self.id in visited:
            return

        visited.add(self.id)
        commercial_partner = self.commercial_partner_id
        sync_vals = commercial_partner._update_fields_values(self._commercial_fields())
        sync_children = self.child_ids.filtered(lambda c: not c.is_company)

        for child in sync_children:
            child._commercial_sync_to_children(visited=visited)

        res = sync_children.write(sync_vals)
        sync_children._compute_commercial_partner()
        return res

    # Partner Flags
    partner_flag_ids = fields.One2many("partner.flag", inverse_name="partner_id")
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

    # Create Users
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

    @api.depends("partner_id.user_ids")
    def _compute_create_users_button(self):
        """Compute the visibility of the 'Create Portal User' button."""
        for record in self:
            record.create_users_button = not bool(record.partner_id.user_ids)

    def create_portal_user(self):
        """Create a portal user for the partner."""
        self.ensure_one()
        if self.user_ids:
            raise UserError(_("A user for this partner already exists."))

        portal_user_group = self.env.ref("base.group_portal")
        group_ids = [portal_user_group.id]

        return {
            "type": "ir.actions.act_window",
            "name": _("Create Login"),
            "view_mode": "form",
            "view_id": self.env.ref("nwpl_odoo_master.view_create_user_wizard_form").id,
            "target": "new",
            "res_model": "res.users",
            "context": {
                "default_partner_id": self.id,
                "default_groups_id": [(6, 0, group_ids)],
            },
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

    # Sales Orders
    sale_order_ids = fields.One2many(
        "sale.order",
        "partner_id",
        string="Sale Orders",
    )

    current_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_current_sale_order_ids",
        string="Current Orders",
        store=False,
    )

    historic_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_historic_sale_order_ids",
        string="Historic Orders",
        store=False,
    )

    reorder_count = fields.Integer(
        compute="_compute_reorder_order_count",
        string="Reorder",
    )

    def _compute_current_sale_order_ids(self):
        """
        Compute method to populate the 'current_sale_order_ids' field.
        Includes all sales orders that are not done or canceled.
        """
        for partner in self:
            partner.current_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state not in ("done", "cancel")
            )

    def _compute_historic_sale_order_ids(self):
        """
        Compute method to populate the 'historic_sale_order_ids' field.
        Includes all sales orders that are done or canceled and can be reordered.
        """
        for partner in self:
            partner.historic_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state in ("done", "cancel") and order.is_reorder
            )

    def _compute_reorder_order_count(self):
        """
        Compute the count of reorderable historic sale orders for the partner.
        """
        for partner in self:
            partner.reorder_count = len(partner.historic_sale_order_ids)

    def open_sale_from_view_action(self):
        """
        Open the sale orders action filtered by reorder sales for the partner.
        """
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [
            ("partner_id", "=", self.id),
            ("state", "=", "sale"),
            ("is_reorder", "=", True),
        ]
        return action
