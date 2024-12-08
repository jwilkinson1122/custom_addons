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
    _inherit = "res.partner"

    ref = fields.Char("Customer Number", readonly=True, default=lambda self: _("New"))

    use_parent_invoice_address = fields.Boolean()

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
    extra_phone = fields.Char()
    secondary_email = fields.Char(string="Secondary Email")
    fax = fields.Char()

    # Boolean Fields
    is_company_parent = fields.Boolean(
        string="Is a Parent Company",
        compute="_compute_is_company_parent",
        store=True,
        help="Indicates if the partner is a parent company.",
    )

    is_supplier = fields.Boolean(string="Is a Supplier", default=False)

    is_contact = fields.Boolean(
        string="Is a Contact",
        compute="_compute_is_contact",
        inverse="_inverse_is_contact",
        store=True,
        help="Indicates if the partner is a contact.",
    )

    is_patient = fields.Boolean(
        string="Is a Patient",
        compute="_compute_is_patient",
        inverse="_inverse_is_patient",
        store=True,
        help="Indicates if the partner is a patient.",
    )

    # Companies (Parent)
    parent_id = fields.Many2one(
        comodel_name="res.partner",
        string="Parent Company",
        index=True,
        domain=[("is_company_parent", "=", True), ("is_company", "=", True)],
    )

    parent_name = fields.Char(
        related="parent_id.name", readonly=True, string="Parent Name"
    )

    highest_parent_id = fields.Many2one(
        "res.partner",
        compute="_compute_highest_parent_id",
        store=True,
        string="Highest Parent",
    )

    @api.depends("parent_id", "affiliate_ids")
    def _compute_is_company_parent(self):
        for rec in self:
            _logger.info(
                f"Computing is_company_parent for {rec.id}: "
                f"parent_id={rec.parent_id}, affiliate_ids={rec.affiliate_ids.ids}"
            )
            if rec.is_company_parent:
                continue
            rec.is_company_parent = (
                rec.company_type == "company"
                and bool(rec.affiliate_ids)
                and not rec.parent_id
            )

    @api.depends("parent_id")
    def _compute_highest_parent_id(self):
        """Compute the highest parent company."""
        for rec in self:
            res = []
            partner = rec
            while partner.parent_id:
                res.append(partner.parent_id.id)
                partner = partner.parent_id
            rec.highest_parent_id = res[-1] if res else None

    @api.model
    def compute_all_top_parent_id(self):
        partner_ids = self.search(
            [("is_company_parent", "=", False), ("parent_id", "!=", False)]
        )
        for partner in partner_ids:
            original_is_company_parent = partner.is_company_parent
            res = partner.compute_partner_parent_ids(rec=partner)
            if res:
                partner.highest_parent_id = res[-1]
            partner.is_company_parent = original_is_company_parent

    # Affiliates (Child)
    affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="parent_id",
        string="Affiliates",
        compute="_compute_affiliate_ids",
        store=False,  # Make it dynamic to reflect changes immediately
    )

    affiliate_count = fields.Integer(
        string="Affiliate Count", compute="_compute_affiliate_and_contact_counts"
    )

    affiliate_text = fields.Char(compute="_compute_affiliate_text")

    @api.depends("affiliate_count")
    def _compute_affiliate_text(self):
        """Generate affiliate count text."""
        for record in self:
            record.affiliate_text = _("%s Affiliates" % record.affiliate_count)

    @api.depends("affiliate_ids")
    def _compute_affiliate_and_contact_counts(self):
        """Compute affiliate and contact counts, including hierarchical affiliates."""
        for record in self:
            # Affiliates that are not parent companies and can themselves have affiliates
            affiliates = record.affiliate_ids.filtered(
                lambda p: not p.is_company_parent or p.affiliate_ids
            )
            record.affiliate_count = len(affiliates)

            # Contacts directly linked to the current partner
            contacts = record.child_ids.filtered(lambda p: p.is_contact)
            record.contact_count = len(contacts)

    @api.depends("parent_id", "affiliate_ids")
    def _compute_affiliate_ids(self):
        """
        Compute all descendant companies as affiliates.
        """
        for partner in self:
            if isinstance(partner.id, models.NewId):  # Handle records not yet saved
                partner.affiliate_ids = self.env["res.partner"].browse()
            else:
                all_descendants = self.env["res.partner"].search(
                    [
                        ("id", "child_of", partner.id),
                        ("id", "!=", partner.id),
                        ("is_company", "=", True),
                    ]
                )
                partner.affiliate_ids = all_descendants

    # Contacts
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

    contact_role_id = fields.Many2one(
        "res.partner.role",
        string="Contact Role",
        help="Refers to general responsibilities within a company.",
    )

    contact_position_id = fields.Many2one(
        "res.partner.position",
        "Contact Position",
        help="Refers to a specific function or responsibilities within a company.",
    )

    contact_count = fields.Integer(
        string="Contact Count", compute="_compute_affiliate_and_contact_counts"
    )

    contact_text = fields.Char(compute="_compute_contact_text")

    @api.depends("contact_id")
    def _compute_is_contact(self):
        """Determine if the partner is a contact."""
        for partner in self:
            partner.is_contact = (
                partner.contact_id.is_contact if partner.contact_id else False
            )

    def _inverse_is_contact(self):
        """Update contact status."""
        for partner in self:
            if partner.contact_id:
                partner.contact_id.is_contact = partner.is_contact

    @api.depends("contact_count")
    def _compute_contact_text(self):
        """Generate contact count text."""
        for record in self:
            record.contact_text = _("%s Contacts" % record.contact_count)

    # Patients
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

    patient_records = fields.One2many(
        "res.contact",
        compute="_compute_patient_records",
        string="Patients",
    )

    patient_count = fields.Integer(
        string="Patient Count", compute="_compute_patient_counts"
    )

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

    @api.depends("child_ids.patient_ids")
    def _compute_patient_counts(self):
        """Compute the patient count."""
        for record in self:
            record.patient_count = len(record.patient_ids)

    @api.depends("child_ids.patient_ids")
    def _compute_patient_records(self):
        """Compute the related patient records."""
        for record in self:
            record.patient_records = record.child_ids.mapped("patient_ids")

    @api.constrains("ref", "is_company", "company_type")
    def _check_ref(self):
        for partner in self.filtered("ref"):
            domain = [
                ("id", "!=", partner.id),
                ("ref", "=", partner.ref),
            ]
            # Check based on partner type to ensure that IDs do not overlap within the same type
            if partner.is_company:
                domain.append(("is_company", "=", True))
            elif partner.is_contact:
                domain.append(("is_contact", "=", True))
            elif partner.is_patient:
                domain.append(("is_patient", "=", True))
            elif partner.parent_id:
                # If it has a parent_id, it's a child or affiliate company
                domain.append(("parent_id", "!=", False))

            other = self.search(domain)
            if other:
                raise ValidationError(
                    _("This reference is equal to partner '%s'") % other[0].display_name
                )

    # @api.constrains("ref", "is_company", "parent_id")
    # def _check_ref(self):
    #     for partner in self.filtered("ref"):
    #         domain = [
    #             ("id", "!=", partner.id),
    #             ("ref", "=", partner.ref),
    #         ]
    #         if partner.is_company:
    #             domain.append(("is_company", "=", True))
    #         other = self.search(domain)
    #         if other:
    #             raise ValidationError(
    #                 _("This reference is equal to partner '%s'") % other[0].display_name
    #             )

    # @api.constrains("ref", "is_company", "company_id")
    # def _check_ref(self):
    #     for partner in self.filtered("ref"):
    #         domain = [
    #             ("id", "!=", partner.id),
    #             ("ref", "=", partner.ref),
    #         ]
    #         if partner.is_company:
    #             domain.append(("is_company", "=", True))
    #         other = self.search(domain)
    #         if other:
    #             raise ValidationError(
    #                 _("This reference is equal to partner '%s'") % other[0].display_name
    #             )

    # @api.model_create_multi
    # def create(self, vals_list):
    #     """Custom create method to handle partner references."""
    #     for vals in vals_list:
    #         if not vals.get("ref") and not vals.get("parent_id"):
    #             vals["ref"] = self.env["ir.sequence"].next_by_code("res.partner")

    #         elif vals.get("parent_id"):
    #             parent = self.browse(vals["parent_id"])
    #             if not parent.ref:
    #                 raise ValidationError(
    #                     _(
    #                         "Parent company must have a reference before creating affiliates."
    #                     )
    #                 )
    #             sibling_refs = self.search([("parent_id", "=", parent.id)]).mapped(
    #                 "ref"
    #             )
    #             next_ref = self._get_next_ref(sibling_refs)
    #             vals["ref"] = f"{parent.ref}/{next_ref}"

    #     return super().create(vals_list)

    @api.model_create_multi
    def create(self, vals_list):
        """Custom create method to handle partner references."""
        for vals in vals_list:
            if vals.get("parent_id"):
                # For affiliate companies, append to parent company ref
                parent = self.browse(vals["parent_id"])
                if not parent.ref:
                    raise ValidationError(
                        _(
                            "Parent company must have a reference before creating affiliates."
                        )
                    )
                sibling_refs = self.search([("parent_id", "=", parent.id)]).mapped(
                    "ref"
                )
                next_ref = self._get_next_ref(sibling_refs)
                vals["ref"] = f"{parent.ref}/{next_ref}"
            else:
                # Generate ref for parent companies, contacts, or patients
                if vals.get("is_company"):
                    vals["ref"] = self.env["ir.sequence"].next_by_code(
                        "res.partner.company"
                    )
                elif vals.get("is_contact"):
                    vals["ref"] = self.env["ir.sequence"].next_by_code(
                        "res.partner.contact"
                    )
                elif vals.get("is_patient"):
                    vals["ref"] = self.env["ir.sequence"].next_by_code(
                        "res.partner.patient"
                    )
                else:
                    vals["ref"] = self.env["ir.sequence"].next_by_code(
                        "res.partner.affiliate"
                    )

        return super().create(vals_list)

    def copy(self, default=None):
        default = default or {}
        if self._needs_ref():
            default["ref"] = self._get_next_ref()
        return super().copy(default=default)

    def write(self, vals):
        """Custom write method to handle references and preserve user settings."""
        # Prevent recursion
        if self.env.context.get("prevent_recursion"):
            return super().write(vals)

        # Recursion prevention context
        context = dict(self.env.context, prevent_recursion=True)

        for partner in self:
            partner_vals = vals.copy()

            # Handle reference updates or generation
            if "ref" in partner_vals or partner_vals.get("ref"):
                partner_vals["ref"] = partner_vals.get(
                    "ref", partner._get_next_ref(vals=partner_vals)
                )
                if partner.child_ids:
                    partner._update_child_references()

            # Preserve original `is_company_parent` value
            original_is_company_parent = partner.is_company_parent

            # Perform the write operation
            super(ResPartner, partner).with_context(context).write(partner_vals)

            # Restore or update `is_company_parent`
            if "is_company_parent" in partner_vals:
                partner.is_company_parent = partner_vals["is_company_parent"]
            else:
                partner.is_company_parent = original_is_company_parent

            # Handle archived partners and their default addresses
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

            # Recompute parent hierarchy if `parent_id` is modified
            if "parent_id" in partner_vals:
                partner.compute_all_top_parent_id()

        return True

    def _update_child_references(self):
        """Update references for child companies."""
        for child in self.child_ids:
            sibling_refs = self.search(
                [("parent_id", "=", self.id), ("id", "!=", child.id)]
            ).mapped("ref")
            next_ref = self._get_next_ref(sibling_refs)
            new_ref = f"{self.ref}/{next_ref}"
            child.write({"ref": new_ref})
            # Recursively update grandchildren
            child._update_child_references()

    def _get_next_ref(self, sibling_refs):
        """Determine the next available numeric reference for child references."""
        references = [
            int(re.search(r"/(\d+)$", ref).group(1))
            for ref in sibling_refs
            if re.search(r"/(\d+)$", ref)
        ]
        return max(references, default=0) + 1

    @api.model
    def _needs_ref(self, vals=None):
        """Check if a sequence value should be assigned to a partner's ref."""
        return vals.get("is_company") or not vals.get("parent_id")

    def unlink(self):
        """Prevent deletion of partners with children."""
        for partner in self:
            if partner.child_ids or partner.sudo().patient_ids:
                raise ValidationError(
                    _("Cannot delete a partner with linked affiliates or patients.")
                )
        return super().unlink()

    @api.model
    def _commercial_fields(self):
        """
        Extend the commercial fields propagated to the partner's contacts.
        Adds 'ref' and 'company_group_id'.
        """
        return super()._commercial_fields() + ["ref", "company_group_id", "company_id"]

    def action_view_company_group_members(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_contacts.action_open_group_members"
        )
        all_child = self.with_context(active_test=False).search(
            [("id", "child_of", self.ids)]
        )
        action["domain"] = [("company_group_id", "in", all_child.ids)]
        return action

    # onchange methods
    @api.onchange("is_company")
    def _onchange_is_company(self):
        # Check the context for default_is_company_parent
        default_is_company_parent = self.env.context.get("default_is_company_parent")
        if default_is_company_parent is not None:
            # Respect the context value if provided
            self.is_company_parent = default_is_company_parent
        else:
            # Default logic if no context value is provided
            if self.is_company and not self.parent_id:
                self.is_company_parent = True
            else:
                self.is_company_parent = False

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
    def _compute_display_name(self):
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

    current_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_current_sale_order_ids",
        store=False,
    )

    def _compute_current_sale_order_ids(self):
        """
        Compute method to populate the 'current_sale_order_ids' field.
        Filters to show sales orders that are current by removing completed and cancelled sales orders
        """
        for partner in self:
            partner.current_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state not in ("done", "cancel")
            )


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
