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

    parent_id = fields.Many2one(
        "res.partner",
        index=True,
        domain=[("is_company", "=", True), ("is_account", "=", True)],
        string="Account",
        groups="base.group_no_one",
    )

    type = fields.Selection(default=False)

    partner_type_id = fields.Many2one(
        "res.partner.type",
        "Partner Type",
        domain="[('company_type', '=', company_type)]",
    )
    can_have_parent = fields.Boolean(compute="_compute_partner_type_infos")
    parent_is_required = fields.Boolean(compute="_compute_partner_type_infos")

    parent_type_ids = fields.Many2many(
        "res.partner.type",
        string="Company types authorized for parent",
        compute="_compute_parent_types",
    )

    contact_ids = fields.One2many(
        "res.partner",
        "parent_id",
        "Contacts",
        domain=[("is_company", "=", False)],
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
            code = "CONTACT"
        self.partner_type_id = self.partner_type_id.search(
            [("code", "=", code)], limit=1
        )

    @api.onchange("partner_type_id")
    def _onchange_partner_type(self):
        self.update(self._get_inherit_values(self.partner_type_id))

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

    @api.model
    def create(self, vals):
        _logger.debug("Creating partner with vals: %s", vals)
        if "partner_type_id" in vals:
            partner_type = self.env["res.partner.type"].browse(vals["partner_type_id"])
            if partner_type:
                vals.update(self._get_inherit_values(partner_type))
        new_partner = super(ResPartner, self).create(vals)
        new_partner._update_children(vals)
        return new_partner

    def write(self, vals):
        _logger.debug("Updating partner with vals: %s", vals)
        partners_by_type = {}
        if vals.get("partner_type_id"):
            partner_type = self.env["res.partner.type"].browse(vals["partner_type_id"])
            partners_by_type[partner_type] = self
        else:
            for partner in self:
                partners_by_type.setdefault(partner.partner_type_id, self.browse())
                partners_by_type[partner.partner_type_id] |= partner
        for partner_type in partners_by_type:
            if list(vals.keys()) != ["is_company"]:  # Avoid infinite loop
                vals.update(self._get_inherit_values(partner_type, not_null=True))
            super(ResPartner, partners_by_type[partner_type]).write(vals)
        self._update_children(vals)
        return True

    @api.constrains("partner_type_id", "parent_id")
    def _check_partner_type_consistency(self):
        for partner in self:
            if partner.parent_id and partner.partner_type_id:
                if (
                    partner.parent_id.partner_type_id
                    not in partner.partner_type_id.parent_type_ids
                ):
                    raise ValidationError(
                        _("Parent partner type is not allowed for this partner type.")
                    )

    def view_affiliates(self):
        return {
            "name": _("Affiliate companies"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "kanban,tree,form",
            "view_id": False,
            "domain": [("parent_id", "in", self.ids), ("is_company", "=", True)],
            "target": "current",
        }

    def _update_fields_view_get_result(self, result, view_type="form"):
        if view_type == "form" and not self._context.get("display_original_view"):
            # In order to inherit all views based on the field order_line
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
        result = super(ResPartner, self).get_view(view_id, view_type, **options)
        node = etree.fromstring(result["arch"])
        view_fields = set(
            el.get("name") for el in node.xpath(".//field[not(ancestor::field)]")
        )
        result["fields"] = self.fields_get(view_fields)
        return self._update_fields_view_get_result(result, view_type)

    @api.model
    def _format_args(self, args):
        if not args:
            return
        for cond in args:
            if (
                isinstance(cond, list)
                and len(cond) == 3
                and isinstance(cond[2], list)
                and cond[2]
            ):
                # Ensure cond[2] is not empty before accessing its first element
                if isinstance(cond[2][0], list):
                    for index, item in enumerate(cond[2]):
                        if isinstance(item, list) and len(item) > 1:
                            if item[0] == 1:  # Replace tuple with ID
                                cond[2][index] = item[1]
                            elif item[0] == 6:  # Replace list with list of IDs
                                cond[2] = item[2]
                                break

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        self._format_args(args)
        return super(ResPartner, self).name_search(name, args, operator, limit)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        self._format_args(args)
        return super(ResPartner, self)._search(args, offset, limit, order, count)

    def _get_display_name_context(self):
        contexts = {}
        for record in self:
            partner = record.with_context(
                show_address=None, show_address_only=None, show_email=None
            )
            contexts[record.id] = {"partner": partner, "_": _}
        return contexts

    @api.depends("partner_type_id.partner_display_name", "name")
    def _compute_display_name(self):
        for record in self:
            # Fallback to the partner's name or "Unnamed" if no name is set
            display_name = record.name or "Unnamed"

            # Check if a custom display name rule is defined
            rule = record.partner_type_id.partner_display_name
            if rule:
                try:
                    # Safely evaluate the rule using the context
                    context = {
                        "partner": record.with_context(
                            show_address=None, show_address_only=None, show_email=None
                        ),
                        "_": _,
                    }
                    _logger.info("Context for display_name: %s", context)
                    display_name = safe_eval(rule, context) or display_name
                    _logger.info("Rule for display_name: %s", rule)
                except Exception as e:
                    _logger.error(
                        "Error evaluating partner display name rule '%s' for partner ID %s: %s",
                        rule,
                        record.id,
                        str(e),
                    )

            # Assign the computed display name
            record.display_name = display_name
