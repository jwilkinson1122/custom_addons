from odoo import models, fields, api, _, Command


class User(models.Model):
    _inherit = "res.users"

    is_treatment_professional = fields.Boolean(
        compute="_compute_is_treatment_professional", store=True
    )

    accessible_practice_ids = fields.Many2many(
        comodel_name="podiatry.practice",
        compute="_compute_accessible_practice_ids",
        inverse="_inverse_accessible_practice_ids",
    )

    @api.depends("groups_id")
    def _compute_is_treatment_professional(self):
        for rec in self:
            rec.is_treatment_professional = rec.has_group(
                "pod_practice_management.group_podiatry_practice_treatment_professional"
            )

    def _compute_accessible_practice_ids(self):
        for rec in self:
            rec.accessible_practice_ids = rec.partner_id.practices_served_ids

    def _inverse_accessible_practice_ids(self):
        for rec in self:
            removed_practices = (
                rec.partner_id.practices_served_ids - rec.accessible_practice_ids
            )
            added_practices = (
                rec.accessible_practice_ids - rec.partner_id.practices_served_ids
            )
            removed_practices = rec.partner_id.practices_served_ids.filtered(
                lambda practice: practice in removed_practices
            )
            removed_practices.remove_access(self)
            self.env["podiatry.practice.staff"].create(
                [
                    {
                        "practice_id": practice.id,
                        "partner_id": rec.partner_id.id,
                        "role": "other",
                    }
                    for practice in added_practices
                ]
            )
