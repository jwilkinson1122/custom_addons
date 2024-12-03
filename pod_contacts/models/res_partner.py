from lxml import etree
import re
import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

INVOICE = "invoice"


def split_char(char, output_number, size):
    words = char.split(" ")
    result = []
    word = words.pop(0)
    for index in range(0, output_number):
        result.append(word)
        word = ""
        while len(words) > 0:
            word = words.pop(0)
            if len(result[index] + " %s" % word) > size:
                break
            else:
                result[index] += " %s" % word
                word = ""
    return result


class ResPartner(models.Model):
    """Add relation affiliate_ids."""

    _inherit = "res.partner"

    use_parent_invoice_address = fields.Boolean()

    highest_parent_id = fields.Many2one(
        "res.partner",
        compute="_get_highest_parent_id",
        store="True",
        string="Highest parent",
    )

    # is_company_parent = fields.Boolean(
    #     string="Is a Parent Company",
    #     default=True,
    #     help="A parent company is a 'Company' type contact for which at least one 'Affiliate' is defined and for which no related company is defined",
    # )

    is_company_parent = fields.Boolean(
        string="Is a Parent Company",
        compute="_compute_is_company_parent",
        inverse="_set_is_company_parent",
        store=True,
        default=True,
        help="Indicates if the partner is a parent company.",
    )

    # is_company_parent = fields.Boolean(
    #     compute="_get_is_company_parent",
    #     store="True",
    #     string="Is a Parent Company",
    #     help="A parent company is a “Company” type contact for which at least "
    #     "one “Affiliate” is defined and for which no related"
    #     " company is defined",
    # )

    company_group_id = fields.Many2one(
        "res.partner",
        domain=[("is_company", "=", True)],
        recursive=True,
    )

    company_group_member_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="company_group_id",
        string="Company group members",
    )

    # Child Companies
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )

    # Contacts
    is_contact = fields.Boolean(
        string="Is a Contact",
        compute="_compute_is_contact",
        inverse="_inverse_is_contact",
        store=True,
        help="Indicates if the partner is a contact.",
    )

    child_ids = fields.One2many(
        domain=[("active", "=", True), ("is_company", "=", False)]
    )

    contact_id = fields.Many2one(
        "res.contact",
        string="Related Contact",
        domain=[("is_contact", "=", True)],
        help="Link to the related contact.",
    )

    contact_role_ids = fields.Many2many(
        string="Contact Roles",
        comodel_name="res.partner.role",
        help="Refers to a general function or responsibilities within a company.",
    )

    contact_position_id = fields.Many2one(
        "res.partner.position",
        "Contact Position",
        help="Refers to a specific function or responsibilities within a company.",
    )

    partner_delivery_id = fields.Many2one(
        comodel_name="res.partner",
        string="Shipping address",
    )

    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice address",
    )

    partner_contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Default contact",
        domain=[("is_company", "=", False)],
    )

    @api.depends("contact_id")
    def _compute_is_contact(self):
        """Synchronize `is_contact` from `res.contact`."""
        for partner in self:
            partner.is_contact = (
                partner.contact_id.is_contact if partner.contact_id else False
            )

    def _inverse_is_contact(self):
        """Update `is_contact` in `res.contact`."""
        for partner in self:
            if partner.contact_id:
                partner.contact_id.is_contact = partner.is_contact

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

    patient_ids = fields.Many2many(
        string="Patients",
        comodel_name="res.contact",
        domain=[("is_patient", "=", True)],
    )

    @api.depends("patient_id")
    def _compute_is_patient(self):
        """Synchronize `is_patient` from `res.contact`."""
        for partner in self:
            partner.is_patient = (
                partner.patient_id.is_patient if partner.patient_id else False
            )

    def _inverse_is_patient(self):
        """Update `is_patient` in `res.contact`."""
        for partner in self:
            if partner.patient_id:
                partner.patient_id.is_patient = partner.is_patient

    zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_zip_id",
        readonly=False,
        store=True,
    )
    city_id = fields.Many2one(
        index=True,
        compute="_compute_city_id",
        readonly=False,
        store=True,
    )
    city = fields.Char(compute="_compute_city", readonly=False, store=True)
    zip = fields.Char(compute="_compute_zip", readonly=False, store=True)
    country_id = fields.Many2one(
        compute="_compute_country_id", readonly=False, store=True
    )
    state_id = fields.Many2one(compute="_compute_state_id", readonly=False, store=True)
    street3 = fields.Char("Street 3")
    fax = fields.Char()

    # @api.depends("company_type", "affiliate_ids", "parent_id")
    # def _get_is_company_parent(self):
    #     """compute if contact is a parent company or not"""
    #     for rec in self:
    #         is_company_parent = False
    #         if (
    #             rec.company_type == "company"
    #             and rec.affiliate_ids
    #             and not rec.parent_id
    #         ):
    #             is_company_parent = True
    #         rec.is_company_parent = is_company_parent

    @api.depends("company_type", "affiliate_ids", "parent_id")
    def _compute_is_company_parent(self):
        """Compute if the contact is a parent company."""
        for rec in self:
            rec.is_company_parent = (
                rec.company_type == "company"
                and bool(rec.affiliate_ids)
                and not rec.parent_id
            )

    def _set_is_company_parent(self):
        """Allow manual override."""
        pass

    def compute_partner_parent_ids(self, rec=False, res=[]):
        if rec.parent_id:
            res.append(rec.parent_id.id)
            self.compute_partner_parent_ids(rec=rec.parent_id, res=res)
        return res

    @api.depends("parent_id", "child_ids")
    def _get_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                res = rec.compute_partner_parent_ids(rec=rec)
                if res:
                    rec.highest_parent_id = res[-1]

    @api.model
    def compute_all_top_parent_id(self):
        partner_ids = self.search(
            [("is_company_parent", "=", False), ("parent_id", "!=", False)]
        )
        for partner in partner_ids:
            res = partner.compute_partner_parent_ids(rec=partner)
            if res:
                partner.highest_parent_id = res[-1]

    @api.constrains("ref", "is_company", "company_id")
    def _check_ref(self):
        for partner in self.filtered("ref"):
            # If the company is not defined in the partner, take current user company
            company = partner.company_id or self.env.company
            mode = company.partner_ref_unique
            # Don't raise when coming from contact merge wizard or no duplicates
            if not self.env.context.get("partner_ref_unique_merging") and (
                mode == "all" or (mode == "companies" and partner.is_company)
            ):
                domain = [
                    ("id", "!=", partner.id),
                    ("ref", "=", partner.ref),
                ]
                if mode == "companies":
                    domain.append(("is_company", "=", True))
                other = self.search(domain)
                if other:
                    raise ValidationError(
                        _("This reference is equal to partner '%s'")
                        % other[0].display_name
                    )

    def _get_next_ref(self, vals=None):
        return self.env["ir.sequence"].next_by_code("res.partner")

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if not vals.get("ref") and self._needs_ref(vals=vals):
    #             vals["ref"] = self._get_next_ref(vals=vals)
    #     return super().create(vals_list)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure `is_company_parent` defaults to `True` for new companies."""
        for vals in vals_list:
            if vals.get("is_company", False) and not vals.get("parent_id"):
                vals["is_company_parent"] = True

            if not vals.get("ref") and self._needs_ref(vals=vals):
                vals["ref"] = self._get_next_ref(vals=vals)
        return super().create(vals_list)

    def copy(self, default=None):
        default = default or {}
        if self._needs_ref():
            default["ref"] = self._get_next_ref()
        return super().copy(default=default)

    def write(self, vals):
        """Custom write method to handle reference generation, parent hierarchy computation,
        and ensure archived contacts are not set as default addresses."""
        for partner in self:
            partner_vals = vals.copy()

            # Handle reference generation if needed
            if (
                not partner_vals.get("ref")
                and partner._needs_ref(vals=partner_vals)
                and not partner.ref
            ):
                partner_vals["ref"] = partner._get_next_ref(vals=partner_vals)

            # Write values
            super(ResPartner, partner).write(partner_vals)

            # Prevent archived contacts as default addresses
            if partner_vals.get("active") is False:
                self.search([("partner_delivery_id", "in", self.ids)]).write(
                    {"partner_delivery_id": False}
                )
                self.search([("partner_invoice_id", "in", self.ids)]).write(
                    {"partner_invoice_id": False}
                )
                self.search([("partner_contact_id", "in", self.ids)]).write(
                    {"partner_contact_id": False}
                )

            # Compute parent hierarchy if parent_id is updated
            if "parent_id" in vals:
                partner.compute_all_top_parent_id()

        return True

    def _needs_ref(self, vals=None):
        """
        Checks whether a sequence value should be assigned to a partner's 'ref'

        :param vals: known field values of the partner object
        :return: true iff a sequence value should be assigned to the\
                      partner's 'ref'
        """
        if not vals and not self:  # pragma: no cover
            raise exceptions.UserError(
                _("Either field values or an id must be provided.")
            )
        # only assign a 'ref' to commercial partners
        fields_for_check = ["is_company", "parent_id"]
        # Copy original vals to prevent modifying them
        if vals:
            vals_for_check = vals.copy()
        else:
            vals_for_check = {}
        if self:
            for field in fields_for_check:
                if field not in vals_for_check:
                    vals_for_check[field] = self[field]
        return vals_for_check.get("is_company") or not vals_for_check.get("parent_id")

    @api.model
    def _commercial_fields(self):
        """
        Extend the commercial fields propagated to the partner's contacts.
        Adds 'ref' and 'company_group_id'.
        """
        return super()._commercial_fields() + ["ref", "company_group_id"]

    def action_view_company_group_members(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_contacts.action_open_group_members"
        )
        all_child = self.with_context(active_test=False).search(
            [("id", "child_of", self.ids)]
        )
        action["domain"] = [("company_group_id", "in", all_child.ids)]
        return action

    @api.onchange("company_group_id")
    def _onchange_company_group_id(self):
        res = {}
        if (
            self.company_group_id
            and self.company_group_id.property_product_pricelist
            != self.property_product_pricelist
        ):
            price_list = self.company_group_id.property_product_pricelist
            res["warning"] = {
                "title": _("Warning"),
                "message": _(
                    "The company group %(company_group)s has"
                    " the pricelist %(pricelist)s, that is different"
                    " than the pricelist set on this contact"
                )
                % {
                    "company_group": self.company_group_id.display_name,
                    "pricelist": price_list.display_name,
                },
            }
        return res

    @api.onchange("property_product_pricelist")
    def _onchange_property_product_pricelist(self):
        res = self._onchange_company_group_id()
        if (
            not res
            and self.company_group_member_ids
            # Need to check _origin because the field company_group_ids is a recordset
            # of NewIds that have False values on the field property_product_pricelist.
            and self.company_group_member_ids._origin.mapped(
                "property_product_pricelist"
            )
            - self.property_product_pricelist
        ):
            company_members = self.company_group_member_ids.filtered(
                lambda cm: cm.property_product_pricelist
                != self.property_product_pricelist
            )
            members_str = ""
            for member in company_members.sorted(key="display_name"):
                members_str += "\t- %s\n" % member.display_name
            res["warning"] = {
                "title": _("Warning"),
                "message": _(
                    "This contact has members of a company group with"
                    f" different pricelists, the members are:\n{members_str}"
                ),
            }
        return res

    @api.depends("state_id", "country_id", "city_id", "zip")
    def _compute_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("zip_id"):
            fields_map = {
                "zip": "name",
                "city_id": "city_id",
                "state_id": "state_id",
                "country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                    record[rec_field]
                    and record[rec_field] != record._origin[rec_field]
                    and record[rec_field] != record.zip_id[zip_field]
                ):
                    record.zip_id = False
                    break

    @api.depends("zip_id")
    def _compute_city_id(self):
        if hasattr(super(), "_compute_city_id"):
            return super()._compute_city_id()  # pragma: no cover
        for record in self:
            if record.zip_id:
                record.city_id = record.zip_id.city_id
            elif not record.country_enforce_cities:
                record.city_id = False

    @api.depends("zip_id")
    def _compute_city(self):
        if hasattr(super(), "_compute_city"):
            return super()._compute_city()  # pragma: no cover
        for record in self:
            if record.zip_id:
                record.city = record.zip_id.city_id.name

    @api.depends("zip_id")
    def _compute_zip(self):
        if hasattr(super(), "_compute_zip"):
            return super()._compute_zip()  # pragma: no cover
        for record in self:
            if record.zip_id:
                record.zip = record.zip_id.name

    @api.depends("zip_id", "state_id")
    def _compute_country_id(self):
        if hasattr(super(), "_compute_country_id"):
            return super()._compute_country_id()  # pragma: no cover
        for record in self:
            if record.zip_id.city_id.country_id:
                record.country_id = record.zip_id.city_id.country_id
            elif record.state_id:
                record.country_id = record.state_id.country_id

    @api.depends("zip_id")
    def _compute_state_id(self):
        if hasattr(super(), "_compute_state_id"):
            return super()._compute_state_id()  # pragma: no cover
        for record in self:
            state = record.zip_id.city_id.state_id
            if state and record.state_id != state:
                record.state_id = record.zip_id.city_id.state_id

    @api.constrains("zip_id", "country_id", "city_id", "state_id", "zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.zip_id.name}
            if rec.zip_id.city_id.country_id != rec.country_id:
                raise ValidationError(
                    self.env._(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s",
                        **error_dict,
                    )
                )
            if rec.zip_id.city_id.state_id != rec.state_id:
                raise ValidationError(
                    self.env._(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s",
                        **error_dict,
                    )
                )
            if rec.zip_id.city_id != rec.city_id:
                raise ValidationError(
                    self.env._(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s",
                        **error_dict,
                    )
                )
            if rec.zip_id.name != rec.zip:
                raise ValidationError(
                    self.env._(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s",
                        **error_dict,
                    )
                )

    def _zip_id_domain(self):
        return """
            [
                ("city_id", "=?", city_id),
                ("city_id.country_id", "=?", country_id),
                ("city_id.state_id", "=?", state_id),
            ]
        """

    @api.model
    def _fields_view_get_address(self, arch):
        # We want to use a domain that requires city_id to be on the view
        # but we can't add it directly there, otherwise _fields_view_get_address
        # in base_address_extended won't do its magic, as it immediately returns
        # if city_id is already in there. On the other hand, if city_id is not in the
        # views, odoo won't let us use it in zip_id's domain.
        # For this reason we need to set the domain here.
        arch = super()._fields_view_get_address(arch)
        doc = etree.fromstring(arch)
        for node in doc.xpath("//field[@name='zip_id']"):
            node.attrib["domain"] = self._zip_id_domain()
        return etree.tostring(doc, encoding="unicode")

    @api.model
    def _address_fields(self):
        res = super()._address_fields() + ["zip_id"]
        res.append("street3")
        return res

    def _display_address(self, without_company=False):
        """Remove empty lines which can happen when street3 field is empty."""
        res = super()._display_address(without_company=without_company)
        while "\n\n" in res:
            res = res.replace("\n\n", "\n")
        return res

    type = fields.Selection(
        [
            ("contact", "Contact Address"),
            ("private", "Private Address"),
            ("patient", "Patient Address"),
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("other", "Other Address"),
        ],
        string="Address Type",
        default="",
        help="- Contact Address: Use this to organize the contact details of employees of a given company (e.g. CEO, CFO, ...).\n"
        "- Patient Address: Use this to organize the contact details of patients of a given company (e.g. patient's home address, ...).\n"
        "- Invoice Address: Preferred address for all invoices. Selected by default when you invoice an order that belongs to this company.\n"
        "- Delivery Address: Preferred address for all deliveries. Selected by default when you deliver an order that belongs to this company.\n"
        "- Private: Private addresses are only visible by authorized users and contain sensitive data (employee home addresses, ...).\n"
        "- Other: Other address for the company (e.g. subsidiary, ...)",
    )

    # type = fields.Selection(
    #     selection_add=[("patient", "Order")], ondelete={"contact": "set default"}
    # )

    # def get_address_default_type(self):
    #     """This will be the extension method for other contact types"""
    #     return ["delivery", "invoice", "contact"]

    def get_address_default_type(self):
        """This will be the extension method for other contact types"""
        return ["delivery", "invoice", "contact", "patient"]

    def address_get(self, adr_pref=None):
        """Get specific addresses based on preferences.
        This method combines custom address logic with the default behavior.
        It considers parent addresses for invoice purposes and uses default addresses
        set on the commercial partner if available.
        """
        res = super().address_get(adr_pref)
        adr_pref = adr_pref or []
        default_address_type_list = {
            x for x in adr_pref if x in self.get_address_default_type()
        }

        for partner in self:
            # Handle default address types based on the commercial partner
            for addr_type in default_address_type_list:
                default_address_id = (
                    partner["partner_{}_id".format(addr_type)]
                    or partner.commercial_partner_id["partner_{}_id".format(addr_type)]
                )
                if default_address_id:
                    res[addr_type] = default_address_id.id

            # Handle parent invoice address if applicable
            commercial_partner = partner.commercial_partner_id
            use_parent_invoice_address = (
                commercial_partner.use_parent_invoice_address
                and commercial_partner.parent_id
            )
            if INVOICE in res and use_parent_invoice_address:
                res[INVOICE] = partner.parent_id.address_get([INVOICE])[INVOICE]

        return res

    def _get_split_address(self, output_number, max_size):
        """This method allows to get a number of street fields according to
        your choice. Default is 2 large fields in Odoo (128 chars).
        In some countries you may use 3 or 4 shorter street fields.

        example:
        res = self.partner_id._get_split_address(3, 35)
        street1, street2, street3 = res
        """
        self.ensure_one()
        street = self.street or ""
        street2 = self.street2 or ""
        if len(street) <= max_size and len(street2) <= max_size:
            result = ["" for i in range(0, output_number)]
            result[0] = street
            result[1] = street2
            return result
        elif len(street) <= max_size:
            return [street] + split_char(street2, output_number - 1, max_size)
        else:
            return split_char(f"{street} {street2}", output_number, max_size)

    @api.onchange("parent_id")
    def _update_use_parent_invoice_address(self):
        if not self.parent_id:
            self.use_parent_invoice_address = False

    @api.depends(
        "complete_name",
        "email",
        "vat",
        "state_id",
        "country_id",
        "commercial_company_name",
    )
    @api.depends_context(
        "show_address",
        "partner_show_db_id",
        "address_inline",
        "show_email",
        "show_vat",
        "lang",
        "_two_lines_partner_address",
        "_keep_partner_address_type",
    )
    def _compute_display_name(self):  # pylint: disable=W8110
        super()._compute_display_name()
        if self.env.context.get("_two_lines_partner_address"):
            for partner in self:
                # Do not split on two lines if name is empty as it would display
                #  the address type on a new line in the report.
                # This happens because Odoo splits the display_name on \n character
                #  and discards the first element to get the address from the
                #  display_name. In which case, the address type would appear as
                #  part of the address.
                if not partner.name and not self.env.context.get(
                    "_keep_partner_address_type"
                ):
                    continue
                displayed_types = partner._complete_name_displayed_types
                type_description = dict(
                    partner._fields["type"]._description_selection(partner.env)
                )
                name = partner.name or ""
                if not name and partner.type in displayed_types:
                    name = type_description[partner.type]
                if name in partner.display_name:
                    pattern = r",\s(?=" + re.escape(name) + ")"
                    partner.display_name = re.sub(pattern, "\n", partner.display_name)

    def open_affiliate_form(self):
        """Open affiliate contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    picking_policy = fields.Selection(
        selection=lambda self: self._get_picking_policy_selection(),
        string="Shipping Policy",
        help="Shipping policy to use in this partner's sales orders. "
        "If you deliver all products at once, the delivery order will be scheduled based "
        "on the greatest product lead time. Otherwise, it will be based on the shortest.",
    )

    @api.model
    def _get_picking_policy_selection(self):
        """Retrieve the selection values for picking_policy."""
        return self.env["sale.order"].fields_get(["picking_policy"])["picking_policy"][
            "selection"
        ]

    create_users_button = fields.Boolean(
        related="contact_id.create_users_button",
        store=False,
    )

    def create_contacts(self):
        """Create a portal user for the partner."""
        self.ensure_one()
        if self.user_ids:
            raise UserError(_("A user for this partner already exists."))

        # Add groups
        # internal_user_group = self.env.ref("base.group_user")
        # group_ids = [internal_user_group.id]

        # Add Portal Groups
        portal_user_group = self.env.ref("base.group_portal")
        portal_patient_group = self.env.ref("group_portal_patient")
        group_ids = [portal_user_group.id, portal_patient_group.id]

        return {
            "type": "ir.actions.act_window",
            "name": _("Create Login"),
            "view_mode": "form",
            "view_id": self.env.ref("pod_contacts.view_create_user_wizard_form").id,
            "target": "new",
            "res_model": "res.users",
            "context": {
                "default_partner_id": self.id,
                "default_groups_id": [(6, 0, group_ids)],
            },
        }


class ResPartnerRole(models.Model):
    _name = "res.partner.role"
    _description = "Contact Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)


class ResPartnerPosition(models.Model):
    _name = "res.partner.position"
    _description = "Contact Positions"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
