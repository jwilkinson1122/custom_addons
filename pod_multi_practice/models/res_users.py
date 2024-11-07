# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import UserError


class Users(models.Model):
    _inherit = "res.users"

    is_internal_user = fields.Boolean(compute="_compute_is_internal_user", store=True)
    practice_ids = fields.Many2many(
        "res.practice", compute="_compute_practice_ids", inverse="_inverse_practice_ids"
    )
    practice_id = fields.Many2one(
        "res.practice", string="Default Practice", domain="[('id', 'in', practice_ids)]"
    )

    @api.depends("groups_id")
    def _compute_is_internal_user(self):
        for user in self:
            user.is_internal_user = user.has_group(
                "pod_multi_practice.group_res_internal_user_podiatry"
            )

    def _compute_practice_ids(self):
        for user in self:
            user.practice_ids = user.partner_id.practices_served_ids

    def _inverse_practice_ids(self):
        for user in self:
            removed_practices = user.partner_id.practices_served_ids - user.practice_ids
            added_practices = user.practice_ids - user.partner_id.practices_served_ids
            removed_practices.remove_access(user)
            self.env["res.practice.contact"].create(
                [
                    {
                        "practice_id": practice.id,
                        "partner_id": user.partner_id.id,
                        "role": "other",
                    }
                    for practice in added_practices
                ]
            )

    @api.constrains("practice_id")
    def _check_practice_company(self):
        company = self.env.company
        for user in self:
            if user.practice_id and user.practice_id.company_id != company:
                raise UserError(
                    _("Selected Practice does not belong to the current company '%s'")
                    % company.name
                )

    def _get_default_warehouse_id(self):
        if self.property_warehouse_id:
            return self.property_warehouse_id
        if len(self.env.user.practice_ids) == 1:
            warehouse = self.env["stock.warehouse"].search(
                [("practice_id", "=", self.env.user.practice_id.id)], limit=1
            )
            if not warehouse:
                warehouse = self.env["stock.warehouse"].search(
                    [("practice_id", "=", False)], limit=1
                )
            if not warehouse:
                raise UserError(
                    _("No warehouse found in '%s' practice")
                    % self.env.user.practice_id.name
                )
            return warehouse
        else:
            return self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )


# class Users(models.Model):
#     _inherit = "res.users"

#     is_internal_user = fields.Boolean(compute="_compute_is_internal_user", store=True)

#     practice_ids = fields.Many2many(
#         comodel_name="res.practice",
#         compute="_compute_practice_ids",
#         inverse="_inverse_practice_ids",
#     )

#     practice_id = fields.Many2one(
#         "res.practice",
#         string="Default Practice",
#         default=False,
#         domain="[('id', '=', practice_ids)]",
#     )

#     @api.depends("groups_id")
#     def _compute_is_internal_user(self):
#         for rec in self:
#             rec.is_internal_user = rec.has_group(
#                 "pod_multi_practice.group_res_internal_user_podiatry"
#             )

#     def _compute_practice_ids(self):
#         for rec in self:
#             rec.practice_ids = rec.partner_id.practices_served_ids

#     def _inverse_practice_ids(self):
#         for rec in self:
#             removed_practices = rec.partner_id.practices_served_ids - rec.practice_ids
#             added_practices = rec.practice_ids - rec.partner_id.practices_served_ids
#             removed_practices = rec.partner_id.practices_served_ids.filtered(
#                 lambda practice: practice in removed_practices
#             )
#             removed_practices.remove_access(self)
#             self.env["res.practice.contact"].create(
#                 [
#                     {
#                         "practice_id": practice.id,
#                         "partner_id": rec.partner_id.id,
#                         "role": "other",
#                     }
#                     for practice in added_practices
#                 ]
#             )

#     @api.constrains("practice_id")
#     def practice_constrains(self):
#         """practice constrains"""
#         company = self.env.company
#         for user in self:
#             if user.practice_id and user.practice_id.company_id != company:
#                 raise exceptions.UserError(
#                     _(
#                         "Sorry! The selected Practice does "
#                         "not belong to the current Company"
#                         " '%s'",
#                         company.name,
#                     )
#                 )

#     def _get_default_warehouse_id(self):
#         """method to get default warehouse id"""
#         if self.property_warehouse_id:
#             return self.property_warehouse_id
#         # !!! Any change to the following search domain should probably
#         # be also applied in sale_stock/models/sale_order.py/_init_column.
#         if len(self.env.user.practice_ids) == 1:
#             warehouse = self.env["stock.warehouse"].search(
#                 [("practice_id", "=", self.env.user.practice_id.id)], limit=1
#             )
#             if not warehouse:
#                 warehouse = self.env["stock.warehouse"].search(
#                     [("practice_id", "=", False)], limit=1
#                 )
#             if not warehouse:
#                 error_msg = _(
#                     "No warehouse could be found in the '%s' practice",
#                     self.env.user.practice_id.name,
#                 )
#                 raise UserError(error_msg)
#             return warehouse
#         else:
#             return self.env["stock.warehouse"].search(
#                 [("company_id", "=", self.env.company.id)], limit=1
#             )
