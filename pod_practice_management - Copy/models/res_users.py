from odoo import models, fields, api, _, Command


class User(models.Model):
    _inherit = "res.users"

    is_internal_user = fields.Boolean(compute="_compute_is_internal_user", store=True)

    practice_ids = fields.Many2many(
        comodel_name="res.practice",
        compute="_compute_practice_ids",
        inverse="_inverse_practice_ids",
    )

    @api.depends("groups_id")
    def _compute_is_internal_user(self):
        for rec in self:
            rec.is_internal_user = rec.has_group(
                "pod_practice_management.group_res_practice_internal_user"
            )

    def _compute_practice_ids(self):
        for rec in self:
            rec.practice_ids = rec.partner_id.practices_served_ids

    def _inverse_practice_ids(self):
        for rec in self:
            removed_practices = rec.partner_id.practices_served_ids - rec.practice_ids
            added_practices = rec.practice_ids - rec.partner_id.practices_served_ids
            removed_practices = rec.partner_id.practices_served_ids.filtered(
                lambda practice: practice in removed_practices
            )
            removed_practices.remove_access(self)
            self.env["res.practice.contact"].create(
                [
                    {
                        "practice_id": practice.id,
                        "partner_id": rec.partner_id.id,
                        "role": "other",
                    }
                    for practice in added_practices
                ]
            )
