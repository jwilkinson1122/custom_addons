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

    partner_type = fields.Many2one(
        string="Partner Type",
        comodel_name="contact.partner.type",
        help="Select the type of partner this belongs to.",
    )

    type = fields.Selection(
        selection_add=[
            ("supplier", "Supplier Address"),
            ("patient", "Patient Address"),
        ],
        ondelete={"contact": "set default"},
    )

    # type = fields.Selection(default=False)
    fax_number = fields.Char(string="Fax")

    partner_relation_label = fields.Char(
        "Partner relation label", translate=True, default="Attached To:", readonly=True
    )

    is_supplier = fields.Boolean(string="Vendor")
    is_partner = fields.Boolean(string="Partner", default=False)
    is_parent_company = fields.Boolean(string="Parent Company", default=False)
    is_company = fields.Boolean(string="Company", default=False)
    is_affiliate_company = fields.Boolean(string="Affiliate", default=False)

    is_commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Set this to True if this contact should be treated as its own trading company, "
        "even if it has a parent company.",
    )

    ref = fields.Char(string="Ref", index=True)
    legacy_customer_code = fields.Char("Legacy ID", readonly=True)
    customer_code = fields.Char("ID", readonly=True, default=lambda self: _("New"))

    parent_id = fields.Many2one(
        "res.partner",
        index=True,
        domain=[
            ("is_parent_company", "=", True),
            ("is_company", "=", True),
            ("id", "!=", id),
        ],
        string="Account",
        groups="base.group_no_one",
    )

    parent_name = fields.Char(
        related="parent_id.name", readonly=True, string="Parent name"
    )

    # Affiliates / Child Companies
    affiliate_ids = fields.One2many(
        "res.partner",
        compute="_compute_affiliate_ids",
        string="Affiliates",
        readonly=True,
    )

    affiliate_count = fields.Integer(
        string="Affiliate Count", compute="_compute_affiliate_and_contact_counts"
    )

    affiliate_text = fields.Char(compute="_compute_affiliate_text")

    # Contacts
    is_contact = fields.Boolean(
        string="Is a Contact",
        compute="_compute_is_contact",
        inverse="_inverse_is_contact",
        store=True,
        help="Indicates if the partner is a contact.",
    )

    child_ids = fields.One2many(
        "res.partner",
        compute="_compute_contacts",
        string="Contacts",
        readonly=True,
        index=True,
    )

    contact_id = fields.Many2one(
        "res.partner",
        string="Related Contact",
        domain=[("is_contact", "=", True)],
        help="Link to the related contact.",
    )

    contact_role_ids = fields.Many2many(string="Roles", comodel_name="contact.role")

    contact_count = fields.Integer(
        string="Contact Count", compute="_compute_affiliate_and_contact_counts"
    )

    contact_text = fields.Char(compute="_compute_contact_text")

    # Patients
    is_patient = fields.Boolean(
        string="Is a Patient",
        compute="_compute_is_patient",
        inverse="_inverse_is_patient",
        store=True,
        help="Indicates if the partner is a patient.",
    )

    patient_id = fields.Many2one(
        "res.contact",
        string="Related Contact",
        domain=[("is_patient", "=", True)],
        help="Link to the related patient.",
    )

    patient_ids = fields.One2many(
        "res.partner", compute="_compute_patients", string="Patients", readonly=True
    )

    patient_count = fields.Integer(
        string="Patient Count", compute="_compute_patient_counts"
    )

    patient_records = fields.One2many(
        "res.partner",
        compute="_compute_patient_records",
        string="Patients",
        index=True,
    )

    patient_text = fields.Char(compute="_compute_patient_text")

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

    def apply_contact_logic(self):
        """Automatically assign a contact based on the parent_id."""
        if self.parent_id:
            # Searching for contacts whose parent_id matches the selected practice
            # Exclude records marked as patients
            contacts = self.env["res.partner"].search(
                [
                    ("is_contact", "=", True),
                    ("is_patient", "=", False),  # Exclude patients
                    ("parent_id", "=", self.parent_id.id),
                ]
            )
            # If any contacts are found, assign the first one to the contact_id
            if contacts:
                self.contact_id = contacts[0]

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """Update the domain of contact based on the selected parent_id."""
        self.apply_contact_logic()
        if self.parent_id:
            # Set the domain to include only contacts whose parent_id matches the selected practice
            # Exclude patients
            return {
                "domain": {
                    "contact_id": [
                        ("is_contact", "=", True),
                        ("is_patient", "=", False),  # Exclude patients
                        ("parent_id", "=", self.parent_id.id),
                    ]
                }
            }
        else:
            # If no parent is selected, revert to the initial domain excluding patients
            return {
                "domain": {
                    "contact_id": [
                        ("is_contact", "=", True),
                        ("is_patient", "=", False),  # Exclude patients
                    ]
                }
            }

    @api.depends("is_commercial_partner", "parent_id")
    def _compute_commercial_partner(self):
        """
        Override the computation of commercial_partner_id to allow a contact to be its own trading company.
        """
        for partner in self:
            if partner.is_commercial_partner or not partner.parent_id:
                partner.commercial_partner_id = partner
            else:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id

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

    root_ancestor = fields.Many2one(
        comodel_name="res.partner",
        string="Root Ancestor",
        compute="_compute_root_ancestor",
        store=True,
        recursive=True,
    )

    @api.depends("parent_id", "parent_id.root_ancestor")
    def _compute_root_ancestor(self):
        for rec in self:
            rec.root_ancestor = rec.parent_id and rec.parent_id.root_ancestor or rec

    child_count = fields.Integer(compute="_compute_child_count", string="# of Child")

    def _compute_child_count(self):
        for partner in self:
            partner.child_count = len(partner.child_ids)

    @api.depends(
        "parent_id", "is_parent_company", "is_company", "is_affiliate_company", "active"
    )
    def _compute_affiliate_ids(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_affiliates = self.env["res.partner"].search(
                    [
                        ("id", "child_of", record.id),
                        ("is_parent_company", "=", False),
                        ("is_company", "=", True),
                        ("is_affiliate_company", "=", True),
                        ("patient_ids", "=", False),
                        ("active", "=", True),
                    ]
                )
                record.affiliate_ids = all_affiliates - record
            else:
                record.affiliate_ids = self.env["res.partner"]

    @api.depends("affiliate_count")
    def _compute_affiliate_text(self):
        for record in self:
            if not record.affiliate_count:
                record.affiliate_text = False
            elif record.affiliate_count == 1:
                record.affiliate_text = _("(1 Affiliate)")
            else:
                record.affiliate_text = _("(%s Affiliates)" % record.affiliate_count)

    @api.depends("parent_id", "is_company", "is_contact", "active")
    def _compute_contacts(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_contacts = self.env["res.partner"].search(
                    [
                        ("id", "child_of", record.id),
                        ("is_company", "=", False),
                        ("is_contact", "=", True),
                        ("patient_ids", "=", False),
                        ("active", "=", True),
                    ]
                )
                record.child_ids = all_contacts
            else:
                record.child_ids = self.env["res.partner"]

    @api.depends("contact_id", "type")
    def _compute_is_contact(self):
        """Determine if the partner is a contact."""
        for partner in self:
            # Explicitly check if the partner's type is 'contact' and ensure no unwanted propagation
            partner.is_contact = bool(partner.type == "contact" and partner.contact_id)

    def _inverse_is_contact(self):
        """Update contact status."""
        for partner in self:
            if partner.contact_id:
                partner.contact_id.is_contact = partner.is_contact

    @api.depends("contact_count")
    def _compute_contact_text(self):
        for record in self:
            if not record.contact_count:
                record.contact_text = False
            elif record.contact_count == 1:
                record.contact_text = _("(1 Contact)")
            else:
                record.contact_text = _("(%s Contacts)" % record.contact_count)

    @api.depends("child_ids", "child_ids.is_company")
    def _compute_affiliate_and_contact_counts(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_partners = self.env["res.partner"].search(
                    [("parent_id", "child_of", record.id)]
                )
                all_partners -= record
                affiliates = all_partners.filtered(lambda p: p.is_company)
                record.affiliate_count = len(affiliates)
                contacts = all_partners.filtered(
                    lambda p: not p.is_company and not p.patient_ids
                )
                record.contact_count = len(contacts)
            else:
                record.affiliate_count = 0
                record.contact_count = 0

    @api.depends("patient_id")
    def _compute_is_patient(self):
        """Determine if the partner is a patient."""
        for partner in self:
            partner.is_patient = (
                partner.patient_id.is_patient if partner.patient_id else False
            )

    def _inverse_is_patient(self):
        """Update patient status."""
        for partner in self:
            if partner.patient_id:
                partner.patient_id.is_patient = partner.is_patient

    @api.depends("child_ids", "child_ids.patient_ids")
    def _compute_patient_counts(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.patient_count = 0  # Assigning a default value for new records
                continue
            if record.is_contact or record.is_company:
                all_partners = self.env["res.partner"].search(
                    [("parent_id", "child_of", record.id)]
                )
                all_partners -= record
                patients = all_partners.mapped("patient_ids")
                record.patient_count = len(patients)
            else:
                record.patient_count = 0

    @api.depends("is_contact", "child_ids.patient_ids")
    def _compute_patient_records(self):
        for record in self:
            record.patient_records = self.env["res.partner"]
            if record.is_contact:
                record.patient_records = self.env["res.partner"].search(
                    [("contact_id", "=", record.id)]
                )
            else:
                if not isinstance(record.id, models.NewId) and record.is_company:
                    all_partners = self.env["res.partner"].search(
                        [("parent_id", "child_of", record.id)]
                    )
                    all_partners -= record
                    record.patient_records = all_partners.mapped("patient_ids")
            _logger.debug(
                f"Computed patient records for {record.id}: {record.patient_records.ids}"
            )

    @api.depends("patient_count")
    def _compute_patient_text(self):
        for record in self:
            if not record.patient_count:
                record.patient_text = False
            elif record.patient_count == 1:
                record.patient_text = _("(1 Patient)")
            else:
                record.patient_text = _("(%s Patients)" % record.patient_count)

    @api.depends("child_ids", "child_ids.is_patient")
    def _compute_patients(self):
        """
        Compute the patient_ids field to list all child partners who are patients.
        """
        for record in self:
            if not isinstance(record.id, models.NewId):
                # Filter child_ids to include only those marked as patients
                patients = record.child_ids.filtered(lambda p: p.is_patient)
                record.patient_ids = patients
            else:
                # If the record is a new ID, set an empty recordset
                record.patient_ids = self.env["res.partner"]

    # Roles
    is_role_required = fields.Boolean(
        compute="_compute_is_role_required",
        inverse="_inverse_is_role_required",
        string="Is Role Required",
        store=False,
    )

    @api.depends("is_contact", "contact_role_ids")
    def _compute_is_role_required(self):
        for record in self:
            record.is_role_required = record.is_contact and not record.contact_role_ids

    def _inverse_is_role_required(self):
        for record in self:
            if record.is_role_required and not record.contact_role_ids:
                raise ValidationError("Roles are required for contacts.")

    @api.constrains("is_contact", "contact_role_ids")
    def _check_contact_roles(self):
        for record in self:
            if record.is_contact and not record.contact_role_ids:
                raise ValidationError(_("Roles are required for contacts."))

    @api.model
    def _get_contact_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    @api.model
    def create(self, vals):
        # Use legacy_customer_code if provided
        if vals.get("legacy_customer_code"):
            vals["customer_code"] = vals["legacy_customer_code"]
        else:
            # Generate sequence code based on type
            if vals.get("is_company"):
                if vals.get("is_parent_company"):
                    vals["customer_code"] = self.env["ir.sequence"].next_by_code(
                        "parent.company.code"
                    ) or _("New")
                elif vals.get("is_affiliate_company"):
                    vals["customer_code"] = self.env["ir.sequence"].next_by_code(
                        "affiliate.company.code"
                    ) or _("New")
            elif vals.get("is_contact"):
                vals["customer_code"] = self.env["ir.sequence"].next_by_code(
                    "contact.code"
                ) or _("New")
            elif vals.get("is_patient"):
                vals["customer_code"] = self.env["ir.sequence"].next_by_code(
                    "patient.code"
                ) or _("New")
            else:
                vals["customer_code"] = self.env["ir.sequence"].next_by_code(
                    "customer.company.code"
                ) or _("New")

        partners = super(Partner, self).create(vals)

        for partner in partners:
            if not partner.customer_rank:
                partner.customer_rank = 1

        return partners

    @api.constrains("legacy_customer_code")
    def _check_unique_legacy_code(self):
        for record in self:
            if record.legacy_customer_code:
                duplicate = self.search(
                    [
                        ("legacy_customer_code", "=", record.legacy_customer_code),
                        ("id", "!=", record.id),
                    ],
                    limit=1,
                )
                if duplicate:
                    raise ValidationError(
                        _(
                            "Legacy Customer Code must be unique. Found duplicate for: %s"
                        )
                        % record.legacy_customer_code
                    )

    @api.model
    def write(self, vals):
        if self.env.context.get("prevent_recursion", False):
            return super(Partner, self).write(vals)
        context = dict(self.env.context, prevent_recursion=True)
        result = super(Partner, self).with_context(context).write(vals)
        for partner in self:
            if partner.is_partner or partner.patient_ids:
                partner.check_contact("write")
        return result

    def unlink(self):
        for partner in self:
            if partner.is_partner or partner.sudo().patient_ids:
                partner.check_contact("unlink")
        return super().unlink()

    def _commercial_sync_to_children(self, visited=None):
        """Handle sync of commercial fields to descendants"""
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
    def default_contact_fields(self):
        fields = [
            "is_partner",
            "is_company",
            "is_parent_company",
            "is_affiliate_company",
            "is_supplier",
            "is_contact",
            "is_patient",
        ]
        # If there's a need to add more fields from parent or other inheriting models, add here.
        return fields

    @api.constrains("is_affiliate_company", "parent_id")
    def check_affiliate_practice(self):
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_check_affiliate_practice"
        )
        if not test_condition:
            return
        for record in self:
            if record.is_affiliate_company and not record.parent_id:
                raise ValidationError(
                    _("Parent Company must be fulfilled on affiliates")
                )

    def check_contact(self, mode="write"):
        if self.env.su:
            return self._check_contact(mode=mode)

    def _check_contact(self, mode="write"):
        if self.sudo().patient_ids:
            self.sudo().patient_ids.check_access_rights(mode)

        checks = [
            (
                self.is_partner,
                self._check_contact_user,
                "nwpl_odoo_master.group_contacts_user",
            ),
            (
                self.is_company,
                self._check_contact_practice,
                "nwpl_odoo_master.group_contacts_configurator",
            ),
            (
                self.is_contact,
                self._check_contact_contact,
                "nwpl_odoo_master.group_contacts_configurator",
            ),
        ]

        for condition, check_method, group in checks:
            if condition and mode != "read" and not check_method():
                _logger.info(
                    "Access Denied by ACLs for operation: %s, uid: %s, model: %s",
                    mode,
                    self._uid,
                    self._name,
                )
                raise AccessError(
                    _(
                        "You are not allowed to %(mode)s Contacts (res.partner) records.",
                        mode=mode,
                    )
                )

    def _check_contact_user(self):
        return self.env.user.has_group("nwpl_odoo_master.group_contacts_user")

    def _check_contact_practice(self):
        return self.env.user.has_group("nwpl_odoo_master.group_contacts_configurator")

    def _check_contact_contact(self):
        return self.env.user.has_group("nwpl_odoo_master.group_contacts_configurator")

    def get_address_default_type(self):
        """Add new order type."""
        res = super().get_address_default_type()
        res.add("order")
        return res

    @api.model
    def default_get(self, fields_list):
        """We want to avoid passing the fields on the contacts of the partner"""
        result = super().default_get(fields_list)
        for field in self.default_contact_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result

    def _get_name(self):
        """
        Utility method to generate the display name for a partner, incorporating
        contextual options like address formatting, email, VAT, and partner ID.
        """
        partner = self
        name = partner.name or ""

        # Append type description if no name and partner type is relevant
        if partner.company_name or partner.parent_id:
            if not name and partner.type == "order":
                type_dict = self.fields_get(["type"])["type"]["selection"]
                name = type_dict.get(partner.type, name)
            if not partner.is_company:
                name = self._get_contact_name(partner, name)

        # Append address if specified in context
        if self._context.get("show_address_only"):
            name = partner._display_address(without_company=True)
        elif self._context.get("show_address"):
            name = f"{name}\n{partner._display_address(without_company=True)}".strip()

        # Remove extra new lines for clean formatting
        name = name.replace("\n\n", "\n")

        # Inline address format if specified in context
        if self._context.get("address_inline"):
            name = ", ".join(filter(None, name.split("\n")))

        # Append email if requested in context
        if self._context.get("show_email") and partner.email:
            name = f"{name} <{partner.email}>"

        # Format as HTML if specified
        if self._context.get("html_format"):
            name = name.replace("\n", "<br/>")

        # Append VAT if requested
        if self._context.get("show_vat") and partner.vat:
            name = f"{name} ‒ {partner.vat}"

        # Append partner ID for unique identification if no specific context format is requested
        if not any(
            self._context.get(key)
            for key in ["show_address_only", "show_address", "address_inline"]
        ):
            name = f"{name} ‒ {partner.id}"

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

    create_users_button = fields.Boolean(
        compute="_compute_create_users_button",
        store=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        index=True,
        tracking=True,
        # required=True,
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
        # portal_patient_group = self.env.ref("group_portal_patient")
        # group_ids = [portal_user_group.id, portal_patient_group.id]
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

    # current_sale_order_ids = fields.One2many(
    #     "sale.order",
    #     compute="_compute_current_sale_order_ids",
    #     store=False,
    # )

    # def _compute_current_sale_order_ids(self):
    #     """
    #     Compute method to populate the 'current_sale_order_ids' field.
    #     Filters to show sales orders that are current by removing completed and cancelled sales orders
    #     """
    #     for partner in self:
    #         partner.current_sale_order_ids = partner.sale_order_ids.filtered(
    #             lambda order: order.state not in ("done", "cancel")
    #         )
