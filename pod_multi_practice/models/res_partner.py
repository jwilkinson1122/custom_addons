# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


from odoo import api, fields, models, _
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

    patient_ids = fields.Many2many(
        "res.patient",
        relation="partner_patient_rel",  # Changed the relation table name
        column1="partner_id",  # Changed the column name to avoid conflict
        column2="patient_id",
        string="Patients",
        tracking=True,
    )

    patient_count = fields.Integer(compute="_compute_patient_count")

    @api.depends("patient_ids.is_active")
    def _compute_patient_counts(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)
            # rec.inactive_count = len(rec.patient_ids.filtered(lambda p: p.is_active))
            # rec.active_count = rec.patient_count - rec.inactive_count

    @api.depends("company_id")
    def _compute_allowed_practice_ids(self):
        """Compute allowed practices based on the user's practices in the same company."""
        user_practices = self.env.user.practice_ids
        for partner in self:
            partner.allowed_practice_ids = (
                user_practices.filtered(
                    lambda p: p.company_id == partner.company_id
                ).ids
                if partner.is_multiple_company and partner.company_id
                else user_practices.ids
            )

    @api.depends("company_id")
    def _compute_is_multiple_company(self):
        """Check if there are multiple companies in the system."""
        company_count = self.env["res.company"].search_count([])
        multi_company = company_count > 1
        for partner in self:
            partner.is_multiple_company = multi_company

    @api.depends("contact_ids.role")
    def _compute_is_practice_manager(self):
        """Determine if the partner has a 'Practice Manager' role."""
        for partner in self:
            partner.is_practice_manager = any(
                contact.role == "manager" for contact in partner.contact_ids
            )

    @api.depends("contact_ids.role")
    def _compute_is_primary_physician(self):
        """Determine if the partner has a 'Primary Physician' role."""
        for partner in self:
            partner.is_primary_physician = any(
                contact.role == "primary_physician" for contact in partner.contact_ids
            )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if "parent_id" in values:
            parent = self.browse(values["parent_id"])
            values["practice_ids"] = [(6, 0, parent.practice_ids.ids)]
        return values

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """Set practices based on the parent's practices when parent is changed."""
        if self.parent_id:
            self.practice_ids = [(6, 0, self.parent_id.practice_ids.ids)]

    def write(self, vals):
        """Override write to update practices and restrict patient name changes."""
        if "practice_ids" in vals:
            new_practices = vals["practice_ids"]
            for partner in self:
                partner.child_ids.write({"practice_ids": new_practices})

        # Restrict patient name change from partner form
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
        """Compute practices served by gathering practices from contacts."""
        for partner in self:
            partner.practices_served_ids = partner.contact_ids.mapped("practice_id")

    def _inverse_practices_served(self):
        """Inverse method to clean up contacts that are not in the practices served."""
        for partner in self:
            partner.contact_ids.filtered(
                lambda contact: contact.practice_id not in partner.practices_served_ids
            ).unlink()


# class Partner(models.Model):
#     _inherit = "res.partner"

#     is_multiple_company = fields.Boolean(
#         compute="_compute_is_multiple_company", string="Multi Company"
#     )
#     is_practice_partner = fields.Boolean(default=False, string="Is a Practice Partner")
#     is_practice_manager = fields.Boolean(compute="_compute_partner_roles", store=True)
#     is_primary_physician = fields.Boolean(compute="_compute_partner_roles", store=True)

#     practice_ids = fields.Many2many(
#         "res.practice",
#         string="Practices",
#         relation="partner_practice_rel",
#         column1="partner_id",
#         column2="practice_id",
#         domain="[('id', 'in', allowed_practice_ids)]",
#     )
#     allowed_practice_ids = fields.Many2many(
#         "res.practice",
#         compute="_compute_allowed_practice_ids",
#         store=True,
#         relation="partner_allowed_practice_rel",
#     )
#     child_practice_ids = fields.One2many(
#         "res.practice", "parent_practice_id", string="Child Practices"
#     )
#     contact_ids = fields.One2many(
#         "res.practice.contact", "partner_id", string="Contacts"
#     )
#     practices_served_ids = fields.One2many(
#         "res.practice",
#         compute="_compute_practices_served",
#         inverse="_inverse_practices_served",
#     )

#     patient_ids = fields.Many2many(
#         "res.patient",
#         relation="res_practice_patient_rel",
#         column1="practice_id",
#         column2="patient_id",
#         tracking=True,
#         string="Patients",
#     )

#     patient_count = fields.Integer(compute="_compute_patient_count")

#     @api.depends("company_id")
#     def _compute_allowed_practice_ids(self):
#         for partner in self:
#             company_practices = self.env.user.practice_ids.filtered(
#                 lambda p: p.company_id == partner.company_id
#             )
#             partner.allowed_practice_ids = (
#                 company_practices.ids
#                 if partner.is_multiple_company and partner.company_id
#                 else self.env.user.practice_ids.ids
#             )

#     @api.model
#     def _compute_is_multiple_company(self):
#         company_count = self.env["res.company"].search_count([])
#         self.is_multiple_company = company_count > 1

#     @api.depends("contact_ids.role")
#     def _compute_partner_roles(self):
#         for partner in self:
#             roles = partner.contact_ids.mapped("role")
#             partner.is_practice_manager = "manager" in roles
#             partner.is_primary_physician = "primary_physician" in roles

#     @api.model
#     def default_get(self, fields_list):
#         values = super().default_get(fields_list)
#         if "parent_id" in values:
#             values["practice_ids"] = [
#                 (6, 0, self.browse(values["parent_id"]).practice_ids.ids)
#             ]
#         return values

#     @api.onchange("parent_id")
#     def _onchange_parent_id(self):
#         if self.parent_id:
#             self.practice_ids = [(6, 0, self.parent_id.practice_ids.ids)]

#     @api.constrains("name")
#     def _check_name_change(self):
#         for partner in self:
#             if partner.patient_ids and not self._context.get("patient_update"):
#                 raise ValidationError(
#                     _("You cannot change the name of a partner linked to patients.")
#                 )

#     def write(self, vals):
#         if "practice_ids" in vals:
#             for partner in self:
#                 partner.child_ids.write({"practice_ids": vals["practice_ids"]})
#                 return super(Partner, self).write(vals)

#     @api.depends("contact_ids.practice_id")
#     def _compute_practices_served(self):
#         for partner in self:
#             partner.practices_served_ids = partner.contact_ids.mapped("practice_id")

#     @api.depends("contact_ids.practice_id")
#     def _inverse_practices_served(self):
#         for partner in self:
#             partner.contact_ids.filtered(
#                 lambda contact: contact.practice_id not in partner.practices_served_ids
#             ).unlink()
