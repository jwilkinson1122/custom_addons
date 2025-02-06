import logging
import json
from lxml import etree
from odoo import api, fields, models, _, exceptions
from odoo.tools import config
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

INVOICE = "invoice"

class Partner(models.Model):
    _inherit = ["res.partner", "incrementing.sequence.mixin"]
    _name = "res.partner"
    _sequence_group = "parent_id"

    # Basic Information
    is_company = fields.Boolean(
        string="Account", default=True, help="Check this box if this is a Company."
    )
    is_account = fields.Boolean(
        string="Account", help="Check this box if this is a Customer Account."
    )
    is_affiliate = fields.Boolean(
        string="Affiliate", help="Check this box if this is a Company Affiliate."
    )
    is_contact = fields.Boolean(
        string="Contact", help="Check this box if this is a Company Contact."
    )
    is_patient = fields.Boolean(
        string="Patient", help="Check this box if this is a Patient."
    )

    # company_id = fields.Many2one(default=lambda self: self._default_company_id())

    # @api.model
    # def _default_company_id(self):
    #     """Return False for other tests or if creating a company."""
    #     context = self.env.context
    #     if (
    #         context.get("creating_from_company")
    #         or config["test_enable"]
    #         and not context.get("test_partner_company_default")
    #     ):
    #         return False
    #     return self.env.company

    parent_id = fields.Many2one(
        "res.partner",
        index=True,
        domain="[('is_company', '=', True), '|', ('is_account', '=', True), ('is_affiliate', '=', True)]",
        string="Account",
    )

    parent_name = fields.Char(
        related="parent_id.name", readonly=True, string="Account Name"
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

    child_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="parent_id",
        domain=[("active", "=", True), ("is_company", "=", False)],
        string="Contacts",
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
    responsible_contact_id = fields.Many2one(
        "res.partner",
        string="Responsible Contact",
        domain=[("active", "=", True), ("is_company", "=", False)],
        context={'responsible_contact_selection': True},
    )

    # context={'responsible_contact_selection': True}

    patient_ids = fields.One2many(
        "res.partner", "parent_id", domain=[("is_patient", "=", True)]
    )
    patients_count = fields.Integer(
        "Number of Patients", compute="_compute_patients_count"
    )
    sub_patient_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Patients",
        compute="_compute_sub_patient_ids",
    )

    can_have_parent = fields.Boolean(compute="_compute_partner_type_infos")
    parent_is_required = fields.Boolean(compute="_compute_partner_type_infos")

    commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Mark as True if this partner acts as its own trading company, even with a parent company.",
    )

    # technical field used for managing commercial fields
    # commercial_partner_id = fields.Many2one(
    #     "res.partner",
    #     string="Commercial Entity",
    #     compute="_compute_commercial_partner",
    #     store=True,
    #     recursive=True,
    #     index=True,
    # )
    # commercial_company_name = fields.Char(
    #     "Company Name Entity", compute="_compute_commercial_company_name", store=True
    # )
    # company_name = fields.Char("Company Name")

    fax_number = fields.Char(string="Fax")
    customer_code = fields.Char(
        string="Customer Code", readonly=True, default=lambda self: _("New")
    )
    legacy_customer_code = fields.Char("Legacy ID", readonly=True)
    parent_relation_label = fields.Char(
        related="partner_type_id.parent_relation_label", readonly=True
    )

    parent_type_ids = fields.Many2many(
        "res.partner.type",
        string="Company types authorized for parent",
        compute="_compute_parent_types",
    )

    use_parent_invoice_address = fields.Boolean(string="Use Parent Invoice Address", default=False)
    use_parent_shipping_address = fields.Boolean(string="Use Parent Shipping Address", default=False)


    # use_parent_invoice_address = fields.Boolean()
    # invoice_address_to_use_id = fields.Many2one(
    #     "res.partner",
    #     "Invoice address to use",
    #     store=True,
    #     readonly=False,
    #     domain="['|', '&', ('type', '=', 'invoice') ,('parent_id', '=', parent_id),"
    #     " ('id', '=', parent_id)]",
    # )



    # use_parent_address = fields.Boolean(string="Use Parent Address", default=False)

    # Related fields to fetch the parent's address if use_parent_address is True
    # parent_street = fields.Char(related="parent_id.street", readonly=True)
    # parent_city = fields.Char(related="parent_id.city", readonly=True)
    # parent_zip = fields.Char(related="parent_id.zip", readonly=True)
    # parent_state_id = fields.Many2one(related="parent_id.state_id", readonly=True)
    # parent_country_id = fields.Many2one(related="parent_id.country_id", readonly=True)

    partner_type_id = fields.Many2one(
        "res.partner.type", "Partner Type", help="Specify the type of partner."
    )

    partner_type_code = fields.Char(
        related="partner_type_id.code", store=True, readonly=True
    )

    partner_company_type = fields.Many2one(
        comodel_name="partner.company.type",
        help="Specify the type of company this belongs to.",
    )

    type = fields.Selection(
        [
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
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("supplier", "Supplier Address"),
            ("other", "Other Address"),
        ],
        string="Company Address Type",
        compute="_compute_company_address_type",
        inverse="_inverse_company_address_type",
        store=True,  # ✅ Ensure the computed value is stored in the database
        # required=True,
    )

    companies_label = fields.Char(
        related="partner_type_id.companies_label", readonly=True
    )

    # Address Defaults
    # partner_invoice_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     string="Invoice address",
    # )

    # partner_delivery_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     string="Shipping address",
    # )
    # partner_supplier_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     string="Supplier address",
    # )

    # partner_other_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     string="Other address",
    # )

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
        sub_affiliates = self.env["res.partner"]
        for affiliate in self.affiliate_ids:
            sub_affiliates |= (
                affiliate.affiliate_ids | affiliate._get_all_sub_affiliates()
            )
        return sub_affiliates

    @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
    def _compute_sub_affiliate_ids(self):
        for partner in self:
            all_sub_affiliates = partner._get_all_sub_affiliates()
            partner.sub_affiliate_ids = all_sub_affiliates - partner.affiliate_ids

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

    # # Constraints
    @api.constrains("parent_id", "partner_type_code", "is_affiliate")
    def _check_no_circular_reference(self):
        for partner in self:
            # Existing circular reference check
            if partner.parent_id == partner:
                # if partner.parent_id and partner.parent_id.id == partner.id:
                raise ValidationError(_("A partner cannot be its own parent."))

            visited = set()
            current = partner.parent_id
            while current:
                if current.id in visited:
                    raise ValidationError(
                        _("Circular reference detected in the hierarchy.")
                    )
                visited.add(current.id)
                current = current.parent_id

            # Additional check for affiliates
            if partner.is_patient and not partner.parent_id:
                raise ValidationError(_("Affiliates must have a parent account."))

    @api.constrains("parent_id", "is_affiliate")
    def _check_affiliate_parent_constraint(self):
        for record in self:
            if record.is_affiliate and not record.parent_id:
                if record.create_date:  # Ensure the record has been saved
                    raise ValidationError(_("Affiliates must have a parent account."))

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

        # Search for the matching partner type dynamically
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
        self.apply_contact_logic()
        domain = [("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))
        return {"domain": {"responsible_contact_id": domain}}

    def apply_contact_logic(self):
        """Assigns responsible contact based on parent."""
        if self.parent_id:
            contacts = self.env["res.partner"].search(
                [("parent_id", "=", self.parent_id.id), ("is_company", "=", False)],
                limit=1,
            )
            self.responsible_contact_id = contacts.id if contacts else False
            _logger.debug(
                f"Assigned responsible_contact_id: {contacts.name if contacts else 'None'}"
            )
        else:
            self.responsible_contact_id = False

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

    # Address
    # @api.onchange("use_parent_invoice_address")
    # def _onchange_use_parent_invoice_address(self):
    #     if not any(child.type == "invoice" for child in self.parent_id.child_ids):
    #         self.invoice_address_to_use_id = self.parent_id
    #     else:
    #         self.invoice_address_to_use_id = False

    # def _update_for_specific_invoice_address(self, res):
    #     if res.get(INVOICE, False):
    #         res[INVOICE] = self.commercial_partner_id.invoice_address_to_use_id.id

    # def address_get(self, adr_pref=None):
    #     res = super().address_get(adr_pref)

    #     commercial_partner = self.commercial_partner_id

    #     use_parent_invoice_address = (
    #         commercial_partner.use_parent_invoice_address
    #         and commercial_partner.parent_id
    #     )

    #     if INVOICE in res and use_parent_invoice_address:
    #         if not self.commercial_partner_id.invoice_address_to_use_id:
    #             # this case is only if record still empty
    #             # even "required" managed on view
    #             res[INVOICE] = self.parent_id.address_get([INVOICE])[INVOICE]
    #         else:
    #             # normally, it shoud only use this case :
    #             # use_parent_invoice_address set to True,
    #             # invoice_address_to_use_id shoud not be empty
    #             self._update_for_specific_invoice_address(res)

    #     return res

    # @api.onchange("parent_id")
    # def _update_use_parent_invoice_address(self):
    #     if not self.parent_id:
    #         self.use_parent_invoice_address = False


    @api.onchange("parent_id", "use_parent_invoice_address", "use_parent_shipping_address")
    def _onchange_parent_address_flags(self):
        _logger.debug(f"Triggered onchange for parent_id: {self.parent_id}, use_parent_invoice_address: {self.use_parent_invoice_address}, use_parent_shipping_address: {self.use_parent_shipping_address}")

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
        """Create a partner and apply address inheritance logic if needed."""
        _logger.debug("Received vals for create: %s", vals)

        if vals.get("parent_id"):
            vals["parent_id"] = int(vals["parent_id"])

        # Generate customer code if it's new
        if vals.get("customer_code", _("New")) == _("New"):
            vals["customer_code"] = self._generate_reference(vals)
            _logger.debug("Generated customer_code: %s", vals["customer_code"])

        partner = super(Partner, self).create(vals)

        # Apply address inheritance logic if needed
        if partner.use_parent_invoice_address or partner.use_parent_shipping_address:
            partner._onchange_parent_address_flags()

        return partner

    def write(self, vals):
        """Update partner and apply relevant changes, including address inheritance and customer code generation."""
        _logger.info("Updating partner(s) with values: %s", vals)

        needs_code_update = any(
            key in vals
            for key in ["parent_id", "is_account", "is_affiliate", "is_contact", "is_patient"]
        )

        for partner in self:
            if needs_code_update or partner.customer_code == _("New"):
                _logger.info("Regenerating customer_code for partner ID: %s", partner.id)
                vals["customer_code"] = self._generate_reference(vals)
                _logger.info("Updated customer_code: %s", vals["customer_code"])

        result = super(Partner, self).write(vals)

        # Apply address inheritance logic if necessary
        if "use_parent_invoice_address" in vals or "use_parent_shipping_address" in vals or "parent_id" in vals:
            self._onchange_parent_address_flags()

        self._validate_affiliate_parent()
        self._update_children(vals)
        _logger.info("Partner(s) updated successfully.")

        return result




    # @api.model
    # def create(self, vals):
    #     _logger.debug("Received vals for create: %s", vals)

    #     if vals.get("parent_id"):
    #         vals["parent_id"] = int(vals["parent_id"])

    #     if vals.get("customer_code", _("New")) == _("New"):
    #         vals["customer_code"] = self._generate_reference(vals)
    #         _logger.debug("Generated customer_code: %s", vals["customer_code"])

    #     return super(Partner, self).create(vals)

    # def write(self, vals):
    #     _logger.info("Updating partner(s) with values: %s", vals)

    #     needs_code_update = any(
    #         key in vals
    #         for key in [
    #             "parent_id",
    #             "is_account",
    #             "is_affiliate",
    #             "is_contact",
    #             "is_patient",
    #         ]
    #     )

    #     for partner in self:
    #         if needs_code_update or partner.customer_code == _("New"):
    #             _logger.info(
    #                 "Regenerating customer_code for partner ID: %s", partner.id
    #             )
    #             vals["customer_code"] = self._generate_reference(vals)
    #             _logger.info("Updated customer_code: %s", vals["customer_code"])

    #     result = super(Partner, self).write(vals)
    #     self._validate_affiliate_parent()
    #     self._update_children(vals)
    #     _logger.info("Partner(s) updated successfully.")

    #     return result

    def _generate_reference(self, vals):
        _logger.debug("Generating reference with vals: %s", vals)

        if isinstance(vals, str):
            return vals

        if not isinstance(vals, dict):
            raise ValidationError(_("Invalid data passed for reference generation."))

        sequence_map = {
            "is_patient": ("res.partner.patient", "PT"),
            "is_account": ("res.partner.account", "AC"),
            "is_affiliate": ("res.partner.affiliate", "AF"),
            "is_contact": ("res.partner.contact", "CT"),
        }

        new_code = ""
        for key, (seq_code, prefix) in sequence_map.items():
            if vals.get(key):
                # Fetch the last used code with the same prefix
                last_partner = self.env["res.partner"].search(
                    [(key, "=", True), ("customer_code", "like", f"{prefix}%")],
                    order="customer_code desc",
                    limit=1,
                )
                last_code = (
                    last_partner.customer_code if last_partner else f"{prefix}000"
                )

                # Extract the number and increment
                number = int(last_code[len(prefix) :]) + 1

                # Generate a new code with padding
                new_code = f"{prefix}{str(number).zfill(4)}"
                return new_code

        # Fallback for generic sequence
        new_code = self.env["ir.sequence"].next_by_code("res.partner.generic")
        if not new_code:
            raise ValidationError(_("Unable to generate generic customer code."))

        return new_code

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
            # Check if we're in the context of selecting a responsible_contact_id
            if self._context.get("responsible_contact_selection"):
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
