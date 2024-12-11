# -*- coding: utf-8 -*-
import logging
import json
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_account = fields.Boolean(
        string="Account",
        default=True,
        help="Check this box if this contact is a customer account (parent account). It can be selected in sales orders.",
    )

    is_affiliate = fields.Boolean(
        string="Affiliate",
        help="Check this box if this contact is an account affiliate (child account). It can be selected in sales orders.",
    )

    is_supplier = fields.Boolean(
        string="Vendor",
        help="Check this box if this contact is a vendor. It can be selected in purchase orders.",
    )

    is_contact = fields.Boolean(
        string="Is Contact",
        compute="_compute_is_contact",
        store=True,
        help="Indicates whether this record is a contact.",
    )

    is_patient = fields.Boolean(
        string="Patient",
        store=True,
        default=False,
    )

    parent_id = fields.Many2one(
        "res.partner",
        index=True,
        domain=[("is_company", "=", True), ("is_account", "=", True)],
        string="Account",
        groups="base.group_no_one",
    )

    # type = fields.Selection(default=False)

    partner_type_id = fields.Many2one(
        "res.partner.type",
        "Partner Type",
        domain="[('company_type', '=', company_type)]",
        default=None,
    )

    type = fields.Selection(
        related="partner_type_id.type",
        string="Address Type",
        store=True,
        readonly=False,
        help="The address type as defined by the partner type.",
    )

    can_have_parent = fields.Boolean(compute="_compute_partner_type_infos")

    parent_is_required = fields.Boolean(compute="_compute_partner_type_infos")

    parent_type_ids = fields.Many2many(
        "res.partner.type",
        string="Company types authorized for parent",
        compute="_compute_parent_types",
    )

    parent_contact_id = fields.Many2one(
        "res.partner",
        string="Responsible Contact",
        domain=[("is_contact", "=", True)],
        help="Select the contact responsible for this patient.",
    )

    contact_ids = fields.One2many(
        "res.partner",
        "parent_id",
        "Contacts",
        domain=[
            ("is_company", "=", False),
            ("is_contact", "=", True),
            ("is_patient", "=", False),
        ],
    )

    patient_ids = fields.One2many(
        "res.partner",
        "parent_id",
        "Patients",
        domain=[
            ("is_company", "=", False),
            ("is_contact", "=", False),
            ("is_patient", "=", True),
        ],
    )

    affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="parent_id",
        string="Affiliate Companies",
        domain=[("is_company", "=", True), ("is_affiliate", "=", True)],
    )

    affiliates_count = fields.Integer(
        "Number of affiliate companies", compute="_compute_affiliates_count"
    )

    affiliates_label = fields.Char(
        related="partner_type_id.affiliates_label", readonly=True
    )

    parent_relation_label = fields.Char(
        related="partner_type_id.parent_relation_label", readonly=True
    )

    @api.depends("type", "parent_id", "is_company")
    def _compute_is_contact(self):
        """
        Compute the value of `is_contact` based on certain conditions.
        Example logic: it's a contact if it has a parent and isn't a company.
        """
        for partner in self:
            partner.is_contact = bool(partner.parent_id) and not partner.is_company

    @api.constrains("is_contact", "is_company")
    def _check_is_contact_logic(self):
        for partner in self:
            if partner.is_contact and partner.is_company:
                raise ValidationError(
                    _("A record cannot be both a contact and a company.")
                )

    @api.constrains("is_patient", "parent_id", "parent_contact_id")
    def _check_patient_contact(self):
        for partner in self:
            if partner.is_patient and not partner.parent_id:
                raise ValidationError(
                    _("A parent company must be selected for a patient.")
                )
            if partner.is_patient and not partner.parent_contact_id:
                raise ValidationError(
                    _("A responsible contact must be selected for a patient.")
                )

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        if self.parent_id:
            contacts = self.env["res.partner"].search(
                [("parent_id", "=", self.parent_id.id), ("is_company", "=", False)]
            )
            self.parent_contact_id = contacts[:1]

    @api.depends("partner_type_id")
    def _compute_parent_types(self):
        self.parent_type_ids = self.partner_type_id.parent_type_ids

    @api.depends("child_ids")
    def _compute_affiliates_count(self):
        affiliates = self.mapped("child_ids").filtered(lambda child: child.is_company)
        self.affiliates_count = len(affiliates)

    @api.depends("partner_type_id")
    def _compute_partner_type_infos(self):
        self.can_have_parent = True
        self.parent_is_required = False
        if self.partner_type_id:
            self.can_have_parent = self.partner_type_id.can_have_parent
            if self.partner_type_id.can_have_parent:
                self.parent_is_required = self.partner_type_id.parent_is_required

    @api.onchange("company_type")
    def _onchange_company_type(self):
        if self.company_type == "company":
            code = (
                "ACCOUNT"
                if self.is_account
                else "AFFILIATE" if self.is_affiliate else "SUPPLIER"
            )
        else:
            code = "CONTACT" if self.is_contact else "PATIENT"
        self.partner_type_id = self.partner_type_id.search(
            [("code", "=", code)], limit=1
        )

    # @api.onchange("company_type")
    # def _onchange_company_type(self):
    #     code = "CONTACT"
    #     if self.company_type == "company":
    #         code = "SUPPLIER" if self.supplier else "CLIENT"
    #     self.partner_type_id = self.partner_type_id.search(
    #         [("code", "=", code)], limit=1
    #     )

    def _onchange_partner_type(self):
        if self.partner_type_id:
            sanitized_values = self._get_inherit_values(self.partner_type_id)
            try:
                self.update(sanitized_values)
            except ValueError as e:
                _logger.error("Error updating values: %s", e)
                raise ValidationError(_("Invalid data for partner type."))

    def _get_inherit_values(self, partner_type):
        """Returns inherited field values from the partner type."""
        if not partner_type:
            return {}
        inherit_values = partner_type.read()[0]
        # Remove 'id' and validate other values
        inherit_values.pop("id", None)
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

    @api.model
    def create(self, vals):
        """
        Override to handle partner type inheritance logic during creation.
        Ensures inherited values from partner type are applied.
        """
        _logger.debug("Creating partner with vals: %s", vals)
        try:
            partner_type = self._get_partner_type(vals.get("partner_type_id"))
            if partner_type:
                vals.update(self._get_inherit_values(partner_type))
            new_partner = super().create(vals)
            new_partner._update_children(vals)
            return new_partner
        except Exception as e:
            _logger.error("Error during partner creation: %s", e)
            raise ValidationError(_("An error occurred while creating the partner."))

    def write(self, vals):
        """
        Override to handle partner type inheritance logic during updates.
        Ensures inherited values from partner type are applied and avoids infinite loops.
        """
        _logger.debug("Updating partner with vals: %s", vals)
        try:
            # Group partners by their types to apply updates efficiently
            partners_by_type = self._group_partners_by_type(vals.get("partner_type_id"))

            for partner_type, partners in partners_by_type.items():
                if list(vals.keys()) != ["is_company"]:  # Avoid infinite loop
                    vals.update(self._get_inherit_values(partner_type, not_null=True))
                super(ResPartner, partners).write(vals)

            self._update_children(vals)
            return True
        except Exception as e:
            _logger.error("Error during partner update: %s", e)
            raise ValidationError(_("An error occurred while updating the partner."))

    def _get_partner_type(self, partner_type_id):
        """
        Retrieve the partner type record based on the provided ID.
        """
        return (
            self.env["res.partner.type"].browse(partner_type_id)
            if partner_type_id
            else None
        )

    def _group_partners_by_type(self, new_partner_type_id):
        """
        Group partners by their types to handle updates more efficiently.

        :param new_partner_type_id: The new partner type ID being applied.
        :return: A dictionary grouping partners by their types.
        """
        partners_by_type = {}
        if new_partner_type_id:
            partner_type = self.env["res.partner.type"].browse(new_partner_type_id)
            partners_by_type[partner_type] = self
        else:
            for partner in self:
                partner_type = partner.partner_type_id
                partners_by_type.setdefault(partner_type, self.browse())
                partners_by_type[partner_type] |= partner
        return partners_by_type

    @api.constrains("partner_type_id", "parent_id")
    def _check_partner_type_consistency(self):
        """Ensure the parent partner type is allowed for the current partner type."""
        for partner in self:
            if partner.parent_id and partner.partner_type_id:
                allowed_parent_types = partner.partner_type_id.parent_type_ids
                if partner.parent_id.partner_type_id not in allowed_parent_types:
                    raise ValidationError(
                        _("Parent partner type is not allowed for this partner type.")
                    )

    def view_affiliates(self):
        """Open a view of affiliate companies."""
        return {
            "name": _("Affiliate companies"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "kanban,tree,form",
            "domain": [("parent_id", "in", self.ids), ("is_company", "=", True)],
            "target": "current",
        }

    def _update_fields_view_get_result(self, result, view_type="form"):
        """Customize the view dynamically."""
        if view_type == "form" and not self._context.get("display_original_view"):
            doc = etree.XML(result["arch"])
            for node in doc.xpath("//field[@name='child_ids']"):
                node.set("name", "contact_ids")
                node.set(
                    "modifiers",
                    json.dumps(
                        {
                            "default_is_account": False,
                            "default_is_affiliate": False,
                            "default_is_supplier": False,
                        }
                    ),
                )
                result["fields"]["contact_ids"] = result["fields"]["child_ids"]
                result["fields"]["contact_ids"].update(
                    self.fields_get(["contact_ids"])["contact_ids"]
                )
            result["arch"] = etree.tostring(doc)
        return result

    def get_view(self, view_id=None, view_type="form", **options):
        """Override to inject dynamic fields into views."""
        result = super().get_view(view_id, view_type, **options)
        doc = etree.fromstring(result["arch"])
        view_fields = {
            el.get("name") for el in doc.xpath(".//field[not(ancestor::field)]")
        }
        result["fields"] = self.fields_get(view_fields)
        return self._update_fields_view_get_result(result, view_type)

    @api.model
    def _format_args(self, args):
        """Format arguments for domain processing."""
        if not args:
            return
        for cond in args:
            if (
                isinstance(cond, list)
                and len(cond) == 3
                and isinstance(cond[2], list)
                and cond[2]
            ):
                if isinstance(cond[2][0], list):
                    for index, item in enumerate(cond[2]):
                        if isinstance(item, list) and len(item) > 1:
                            cond[2][index] = item[1] if item[0] == 1 else item[2]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Override to format arguments for domain processing."""
        args = args or []
        self._format_args(args)
        return super().name_search(name, args, operator, limit)

    def _search(self, args, offset=0, limit=None, order=None, count=False):
        sanitized_args = [
            arg for arg in args if not isinstance(arg[0], str) or arg[0] in self._fields
        ]
        return super()._search(sanitized_args, offset, limit, order, count)

    def _get_display_name_context(self):
        """Get context for display name computation."""
        return {
            record.id: {
                "partner": record.with_context(
                    show_address=None, show_address_only=None, show_email=None
                ),
                "_": _,
            }
            for record in self
        }

    @api.depends("partner_type_id.partner_display_name", "name")
    def _compute_display_name(self):
        """Compute the display name dynamically."""
        for record in self:
            display_name = record.name or _("Unnamed")
            rule = record.partner_type_id.partner_display_name
            if rule:
                try:
                    context = {
                        "partner": record.with_context(
                            show_address=None, show_address_only=None, show_email=None
                        ),
                        "_": _,
                    }
                    display_name = safe_eval(rule, context) or display_name
                except Exception as e:
                    _logger.error(
                        "Error evaluating display name rule '%s' for partner ID %s: %s",
                        rule,
                        record.id,
                        str(e),
                    )
            record.display_name = display_name

    def _get_partner_type(self, partner_type_id):
        """Helper to fetch partner type safely."""
        return (
            self.env["res.partner.type"].browse(partner_type_id)
            if partner_type_id
            else None
        )
