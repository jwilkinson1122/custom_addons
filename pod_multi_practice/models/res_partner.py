# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    is_multiple_company = fields.Boolean(
        compute="_compute_is_multiple_company", string="Multi Company"
    )
    is_practice_partner = fields.Boolean(default=False, string="Is a Practice Partner")
    is_practice_manager = fields.Boolean(
        compute="_compute_is_practice_manager", store=True
    )
    is_primary_physician = fields.Boolean(
        compute="_compute_is_primary_physician", store=True
    )
    practice_ids = fields.Many2many(
        "res.practice",
        string="Practices",
        relation="partner_practice_rel",
        column1="partner_id",
        column2="practice_id",
        domain="[('id', 'in', allowed_practice_ids)]",
    )
    allowed_practice_ids = fields.Many2many(
        "res.practice",
        compute="_compute_allowed_practice_ids",
        store=True,
        relation="partner_allowed_practice_rel",
    )
    child_practice_ids = fields.One2many(
        "res.practice", "parent_practice_id", string="Child Practices"
    )
    contact_ids = fields.One2many(
        "res.practice.contact", "partner_id", string="Contacts"
    )
    practices_served_ids = fields.One2many(
        "res.practice",
        compute="_compute_practices_served",
        inverse="_inverse_practices_served",
    )

    @api.depends("company_id")
    def _compute_allowed_practice_ids(self):
        for partner in self:
            company_practices = self.env.user.practice_ids.filtered(
                lambda p: p.company_id == partner.company_id
            )
            partner.allowed_practice_ids = (
                company_practices.ids
                if partner.is_multiple_company and partner.company_id
                else self.env.user.practice_ids.ids
            )

    @api.depends("company_id")
    def _compute_is_multiple_company(self):
        company_count = self.env["res.company"].search_count([])
        for partner in self:
            partner.is_multiple_company = company_count > 1

    @api.depends("contact_ids.role")
    def _compute_is_practice_manager(self):
        """Determines if the partner has a role of 'Practice Manager'."""
        for partner in self:
            partner.is_practice_manager = any(
                contact.role == "manager" for contact in partner.contact_ids
            )

    @api.depends("contact_ids.role")
    def _compute_is_primary_physician(self):
        """Determines if the partner has a role of 'Primary Physician'."""
        for partner in self:
            partner.is_primary_physician = any(
                contact.role == "primary_physician" for contact in partner.contact_ids
            )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if "parent_id" in values:
            values["practice_ids"] = [
                (6, 0, self.browse(values["parent_id"]).practice_ids.ids)
            ]
        return values

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        if self.parent_id:
            self.practice_ids = [(6, 0, self.parent_id.practice_ids.ids)]

    def write(self, vals):
        if "practice_ids" in vals:
            new_practices = vals["practice_ids"]
            for partner in self:
                partner.child_ids.write({"practice_ids": new_practices})

        if (
            self.patient_ids
            and "name" in vals
            and not self._context.get("patient_update")
        ):
            raise ValidationError(
                _("To change a patient's name, update from the patient form.")
            )
        return super().write(vals)

    @api.depends("contact_ids.practice_id")
    def _compute_practices_served(self):
        for partner in self:
            partner.practices_served_ids = partner.contact_ids.mapped("practice_id")

    @api.depends("contact_ids.practice_id")
    def _inverse_practices_served(self):
        for partner in self:
            partner.contact_ids.filtered(
                lambda contact: contact.practice_id not in partner.practices_served_ids
            ).unlink()


# class Partner(models.Model):
#     _inherit = "res.partner"

#     is_practice_partner = fields.Boolean("Is a Practice Partner", default=False)

#     practice_ids = fields.Many2many(
#         "res.practice",
#         string="Practices",
#         help="The practices associated with this partner.",
#         relation="partner_practice_rel",
#         column1="partner_id",
#         column2="practice_id",
#         domain="[('id', 'in', allowed_practice_ids)]",
#     )

#     allowed_practice_ids = fields.Many2many(
#         "res.practice",
#         store=True,
#         string="Allowed Practices",
#         compute="_compute_allowed_practice_ids",
#         relation="partner_allowed_practice_rel",
#         column1="partner_id",
#         column2="allowed_practice_id",
#     )

#     is_multiple_company = fields.Boolean(
#         string="Multi Company", compute="_compute_is_multiple_company"
#     )

#     @api.depends("company_id")
#     def _compute_allowed_practice_ids(self):
#         for partner in self:
#             if partner.is_multiple_company:
#                 if partner.company_id:
#                     practice_ids = [
#                         practice.id
#                         for practice in self.env.user.practice_ids
#                         if practice.company_id == partner.company_id
#                     ]
#                     partner.allowed_practice_ids = practice_ids
#                 else:
#                     partner.allowed_practice_ids = self.env.user.practice_ids.ids
#             else:
#                 partner.allowed_practice_ids = self.env.user.practice_ids.ids

#     @api.depends("company_id")
#     def _compute_is_multiple_company(self):
#         """checking is this multi company or not"""
#         for rec in self:
#             rec.is_multiple_company = False
#             company_count = self.env["res.company"].search_count([])
#             if company_count > 1:
#                 rec.is_multiple_company = True

#     @api.model
#     def default_get(self, default_fields):
#         """Add the company of the parent as default if we are creating a
#         child partner.Also take the parent lang by default if any, otherwise,
#         fallback to default DB lang."""
#         values = super().default_get(default_fields)
#         parent = self.env["res.partner"]
#         if "parent_id" in default_fields and values.get("parent_id"):
#             parent = self.browse(values.get("parent_id"))
#             values["practice_id"] = parent.practice_id.id
#         return values

#     @api.onchange("parent_id", "practice_id")
#     def _onchange_parent_id(self):
#         """method to set practice on changing the parent company"""
#         if self.parent_id:
#             self.practice_id = self.parent_id.practice_id.id

#     def write(self, vals):
#         """override write method"""
#         if vals.get("practice_id"):
#             practice_id = vals["practice_id"]
#             for partner in self:
#                 for child in partner.child_ids:
#                     child.write({"practice_id": practice_id})
#         else:
#             for partner in self:
#                 for child in partner.child_ids:
#                     child.write({"practice_id": False})
#         result = super(Partner, self).write(vals)
#         return result
