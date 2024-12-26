import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_module_resource

import logging

_logger = logging.getLogger(__name__)


class Practice(models.Model):
    _name = "podiatry.practice"
    _description = "Medical Practice"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _inherits = {"res.partner": "partner_id"}
    _order = "sequence, id"

    # Parent and Hierarchy
    _parent_name = "parent_id"
    _parent_store = True

    parent_path = fields.Char(
        string="Parent Path",
        compute="_compute_parent_path",
        index=True,
    )
    parent_id = fields.Many2one(
        comodel_name="podiatry.practice",
        string="Parent Practice",
        index=True,
        ondelete="cascade",
        domain="[('company_id', '=', company_id)]",
    )
    child_ids = fields.One2many(
        comodel_name="podiatry.practice",
        inverse_name="parent_id",
        string="Sub Practices",
    )
    child_count = fields.Integer(
        string="Subpractice Count",
        compute="_compute_child_count",
    )

    # General Fields
    active = fields.Boolean(string="Active", default=True, tracking=True)
    name = fields.Char(string="Practice Name", index=True, required=True)
    sequence = fields.Integer(string="Sequence", required=True, default=5)
    code = fields.Char(string="Code", copy=False)
    reference = fields.Char(
        string="Practice Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    full_name = fields.Char(
        string="Full Name",
        compute="_compute_full_name",
        store=True,
    )
    color = fields.Integer(string="Color Index (0-15)")
    notes = fields.Text(string="Notes")

    # Address Fields
    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Telephone")
    mobile = fields.Char(string="Mobile")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    zip = fields.Char(string="ZIP Code")
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        default=lambda self: self.env.company.country_id,
    )
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="State",
        default=lambda self: self.env.company.state_id,
    )
    practice_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Address",
    )

    # Relations
    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        ondelete="restrict",
        help="Partner-related data of the Practice",
    )
    specialty_id = fields.Many2one(
        comodel_name="podiatry.specialty",
        string="Specialty",
    )
    other_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="podiatry_practice_partners_rel",
        column1="practice_id",
        column2="partner_id",
        string="Other Contacts",
    )
    practice_id = fields.Many2many(
        comodel_name="res.partner",
        domain=[("is_company", "=", True)],
        string="Practice",
        required=True,
    )
    practitioner_id = fields.One2many(
        comodel_name="podiatry.practitioner",
        inverse_name="practice_id",
        string="Practitioners",
    )
    patient_ids = fields.One2many(
        comodel_name="podiatry.patient",
        inverse_name="practice_id",
        string="Patients",
    )
    practice_prescription_id = fields.One2many(
        comodel_name="podiatry.prescription",
        inverse_name="practice_id",
        string="Prescriptions",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Created by",
    )

    # Computed Fields
    same_reference_practice_id = fields.Many2one(
        comodel_name="podiatry.practice",
        string="Practice with same Identity",
        compute="_compute_same_reference_practice_id",
    )

    # Default Image
    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            "podiatry", "static/src/img", "company_image.png"
        )
        return base64.b64encode(open(image_path, "rb").read())

    # Field Computations
    @api.depends("parent_id")
    def _compute_parent_path(self):
        for record in self:
            record.parent_path = (
                f"{record.parent_id.parent_path}/{record.id}"
                if record.parent_id
                else str(record.id)
            )

    @api.depends("child_ids")
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)

    @api.depends("name", "parent_id.full_name")
    def _compute_full_name(self):
        for record in self:
            record.full_name = (
                f"{record.parent_id.full_name} / {record.name}"
                if record.parent_id
                else record.name
            )

    @api.depends("reference")
    def _compute_same_reference_practice_id(self):
        for record in self:
            domain = [("reference", "=", record.reference)]
            if record.id:
                domain.append(("id", "!=", record.id))
            record.same_reference_practice_id = (
                self.env["podiatry.practice"].sudo().search(domain, limit=1)
            )

    # Overrides
    @api.model
    def create(self, vals):
        if not vals.get("name"):
            raise ValidationError(_("The Practice Name is required."))
        if vals.get("reference", _("New")) == _("New"):
            vals["reference"] = self.env["ir.sequence"].next_by_code(
                "podiatry.practice"
            ) or _("New")
        if not vals.get("partner_id"):
            partner_vals = {"name": vals["name"], "is_company": True}
            partner = self.env["res.partner"].create(partner_vals)
            vals["partner_id"] = partner.id
        return super(Practice, self).create(vals)

    def write(self, vals):
        if "name" in vals and not vals["name"]:
            raise ValidationError(_("The Practice Name cannot be empty."))
        return super(Practice, self).write(vals)

    def copy(self, default=None):
        raise UserError(_("You cannot duplicate a practice."))

    # Actions
    def action_open_prescriptions(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Prescriptions",
            "res_model": "podiatry.prescription",
            "domain": [("practice_id", "=", self.id)],
            "context": {"default_practice_id": self.id},
            "view_mode": "kanban,tree,form",
            "target": "current",
        }

    # Onchange Methods
    @api.onchange("practice_id")
    def _onchange_practice(self):
        self.practice_address_id = self.practice_id


# class Practice(models.Model):
#     _name = "podiatry.practice"
#     _description = "Medical Practice"
#     _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
#     _inherits = {"res.partner": "partner_id"}
#     _order = "sequence,id"

#     _parent_name = "parent_id"
#     _parent_store = True

#     parent_path = fields.Char(
#         string="Parent Path", compute="_compute_parent_path", index=True
#     )

#     parent_id = fields.Many2one(
#         comodel_name="podiatry.practice",
#         string="Parent Practice",
#         index=True,
#         ondelete="cascade",
#         domain="[('company_id', '=', company_id)]",
#     )

#     @api.depends("parent_id")
#     def _compute_parent_path(self):
#         for record in self:
#             record.parent_path = (
#                 f"{record.parent_id.parent_path}/{record.id}"
#                 if record.parent_id
#                 else str(record.id)
#             )

#     active = fields.Boolean(string="Active", default=True, tracking=True)

#     color = fields.Integer(string="Color Index (0-15)")

#     sequence = fields.Integer(
#         string="Sequence",
#         required=True,
#         default=5,
#     )

#     code = fields.Char(string="Code", copy=False)

#     name = fields.Char(string="Company Name", index=True, required=True)

#     full_name = fields.Char(
#         string="Full Name",
#         compute="_compute_full_name",
#         store=True,
#     )

#     reference = fields.Char(
#         string="Practice Reference",
#         required=True,
#         copy=False,
#         readonly=True,
#         default=lambda self: _("New"),
#     )
#     email = fields.Char(string="E-mail")
#     phone = fields.Char(string="Telephone")
#     mobile = fields.Char(string="Mobile")
#     street = fields.Char(string="Street")
#     street2 = fields.Char(string="Street 2")
#     country_id = fields.Many2one(
#         comodel_name="res.country",
#         string="Country",
#         default=lambda self: self.env.company.country_id,
#     )
#     state_id = fields.Many2one(
#         comodel_name="res.country.state",
#         string="State",
#         default=lambda self: self.env.company.state_id,
#     )
#     city = fields.Char(string="City")
#     zip = fields.Char(string="ZIP Code")

#     notes = fields.Text(string="Notes")

#     @api.depends("name", "parent_id.full_name")
#     def _compute_full_name(self):
#         for practice in self:
#             if practice.parent_id:
#                 practice.full_name = "%s / %s" % (
#                     practice.parent_id.full_name,
#                     practice.name,
#                 )
#             else:
#                 practice.full_name = practice.name
#         return

#     patient_ids = fields.One2many(
#         comodel_name="podiatry.patient",
#         inverse_name="practice_id",
#         string="Patients",
#     )

#     practice_id = fields.Many2many(
#         "res.partner",
#         domain=[("is_company", "=", True)],
#         string="Practice",
#         required=True,
#     )

#     practitioner_id = fields.One2many(
#         comodel_name="podiatry.practitioner",
#         inverse_name="practice_id",
#         string="Contacts",
#     )

#     user_id = fields.Many2one(
#         comodel_name="res.users",
#         string="Created by",
#     )

#     practice_prescription_id = fields.One2many(
#         comodel_name="podiatry.prescription",
#         inverse_name="practice_id",
#         string="Prescriptions",
#     )

#     @api.onchange("practice_id")
#     def _onchange_practice(self):
#         """
#         The purpose of the method is to define a domain for the available
#         purchase orders.
#         """
#         address_id = self.practice_id
#         self.practice_address_id = address_id

#     partner_id = fields.Many2one(
#         "res.partner",
#         string="Related Partner",
#         ondelete="restrict",
#         help="Partner-related data of the Practice",
#     )

#     specialty_id = fields.Many2one(
#         comodel_name="podiatry.specialty", string="specialty"
#     )

#     other_partner_ids = fields.Many2many(
#         comodel_name="res.partner",
#         relation="podiatry_practice_partners_rel",
#         column1="practice_id",
#         column2="partner_id",
#         string="Other Contacts",
#     )

#     company_id = fields.Many2one(
#         comodel_name="res.company",
#         string="Company",
#         index=True,
#         default=lambda self: self.env.company,
#     )

#     practice_address_id = fields.Many2one(
#         "res.partner",
#         string="Address",
#     )

#     child_ids = fields.One2many(
#         comodel_name="podiatry.practice",
#         inverse_name="parent_id",
#         string="Practices",
#     )

#     child_count = fields.Integer(
#         string="Subpractice Count",
#         compute="_compute_child_count",
#     )

#     @api.depends("child_ids")
#     def _compute_child_count(self):
#         for practice in self:
#             practice.child_count = len(practice.child_ids)
#         return

#     same_reference_practice_id = fields.Many2one(
#         comodel_name="podiatry.practice",
#         string="Practice with same Identity",
#         compute="_compute_same_reference_practice_id",
#     )

#     @api.depends("reference")
#     def _compute_same_reference_practice_id(self):
#         for practice in self:
#             domain = [
#                 ("reference", "=", practice.reference),
#             ]

#             origin_id = practice._origin.id

#             if origin_id:
#                 domain += [("id", "!=", origin_id)]

#             practice.same_reference_practice_id = bool(
#                 practice.reference
#             ) and self.with_context(active_test=False).sudo().search(domain, limit=1)

#     @api.model
#     def _default_image(self):
#         image_path = get_module_resource(
#             "podiatry", "static/src/img", "company_image.png"
#         )
#         return base64.b64encode(open(image_path, "rb").read())

#     def _valid_field_parameter(self, field, name):
#         return name == "sort" or super()._valid_field_parameter(field, name)

#     @api.model
#     def create(self, vals):
#         if not vals.get("name"):
#             raise ValidationError(_("The Practice Name (name) is required."))

#         if vals.get("reference", _("New")) == _("New"):
#             vals["reference"] = self.env["ir.sequence"].next_by_code(
#                 "podiatry.practice"
#             ) or _("New")

#         if not vals.get("partner_id"):
#             partner_vals = {
#                 "name": vals["name"],
#                 "is_company": True,
#             }
#             partner = self.env["res.partner"].create(partner_vals)
#             vals["partner_id"] = partner.id

#         practice = super(Practice, self).create(vals)
#         return practice

#     def name_get(self):
#         result = []
#         for rec in self:
#             name = "[" + rec.reference + "] " + rec.name
#             result.append((rec.id, name))
#         return result

#     def write(self, vals):
#         if "name" in vals and not vals["name"]:
#             raise ValidationError(_("The Practice Name (name) cannot be empty."))
#         return super(Practice, self).write(vals)

#     def copy(self, default=None):
#         for rec in self:
#             raise UserError(_("You Can Not Duplicate practice."))

#     def action_open_prescriptions(self):
#         return {
#             "type": "ir.actions.act_window",
#             "name": "Prescriptions",
#             "res_model": "podiatry.prescription",
#             "domain": [("practice_id", "=", self.id)],
#             "context": {"default_practice_id": self.id},
#             "view_mode": "kanban,tree,form",
#             "target": "current",
#         }
