# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PracticePartner(models.Model):
    _inherit = "res.partner"

    is_practice_partner = fields.Boolean("Is a Practice Partner", default=False)

    # practice_ids = fields.Many2many(
    #     "res.practice",
    #     string="Practices",
    #     help="Practices associated with this partner.",
    #     domain="[('id', 'in', allowed_practice_ids)]",
    # )

    # allowed_practice_ids = fields.Many2many(
    #     "res.practice",
    #     string="Allowed Practices",
    #     compute="_compute_allowed_practice_ids",
    #     store=True,
    # )

    practice_ids = fields.Many2many(
        "res.practice",
        string="Practices",
        help="The practices associated with this partner.",
        relation="partner_practice_rel",
        column1="partner_id",
        column2="practice_id",
        domain="[('id', 'in', allowed_practice_ids)]",
    )

    allowed_practice_ids = fields.Many2many(
        "res.practice",
        store=True,
        string="Allowed Practices",
        compute="_compute_allowed_practice_ids",
        relation="partner_allowed_practice_rel",
        column1="partner_id",
        column2="allowed_practice_id",
    )

    is_multiple_company = fields.Boolean(
        string="Multi Company", compute="_compute_is_multiple_company"
    )

    @api.depends("company_id")
    def _compute_allowed_practice_ids(self):
        for partner in self:
            if partner.is_multiple_company and partner.company_id:
                practice_ids = [
                    practice.id
                    for practice in self.env.user.practice_ids
                    if practice.company_id == partner.company_id
                ]
                partner.allowed_practice_ids = practice_ids
            else:
                partner.allowed_practice_ids = self.env.user.practice_ids.ids

    @api.depends("company_id")
    def _compute_is_multiple_company(self):
        """Check if multiple companies exist"""
        company_count = self.env["res.company"].search_count([])
        for rec in self:
            rec.is_multiple_company = company_count > 1

    @api.model
    def default_get(self, default_fields):
        """Add the parent’s practice if creating a child partner."""
        values = super().default_get(default_fields)
        if "parent_id" in values:
            parent = self.browse(values["parent_id"])
            values["practice_ids"] = [(6, 0, parent.practice_ids.ids)]
        return values

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """Set practice based on parent company change."""
        if self.parent_id:
            self.practice_ids = [(6, 0, self.parent_id.practice_ids.ids)]

    def write(self, vals):
        """Override write method to propagate practice changes to children."""
        if "practice_ids" in vals:
            new_practice_ids = vals["practice_ids"]
            for partner in self:
                for child in partner.child_ids:
                    child.write({"practice_ids": new_practice_ids})
        return super(PracticePartner, self).write(vals)


# class PracticePartner(models.Model):
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
#         result = super(PracticePartner, self).write(vals)
#         return result
