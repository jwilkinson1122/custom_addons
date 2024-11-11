from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    # parent_id = fields.Many2one("res.partner", string="Related Company", index=True)
    # parent_name = fields.Char(
    #     related="parent_id.name", readonly=True, string="Parent name"
    # )
    # child_ids = fields.One2many(
    #     "res.partner", "parent_id", string="Contact", domain=[("active", "=", True)]
    # )

    parent_practice_id = fields.Many2one(
        "podiatry.practice", string="Related Practice", index=True
    )

    owned_practice_ids = fields.One2many(
        comodel_name="podiatry.practice", inverse_name="parent_id"
    )
    staff_ids = fields.One2many(
        comodel_name="podiatry.practice.staff", inverse_name="practice_id"
    )
    practice_staff_rel_ids = fields.One2many(
        comodel_name="podiatry.practice.staff",
        inverse_name="partner_id",
        string="Employer(s)",
        help="The practices this person works for.",
    )
    practices_served_ids = fields.One2many(
        comodel_name="podiatry.practice",
        compute="_compute_practices_served",
        inverse="_inverse_practices_served",
    )
    patient_ids = fields.One2many(
        comodel_name="podiatry.patient", inverse_name="partner_id"
    )

    # is_manager = fields.Boolean(compute="_compute_is_manager", store=True)
    # is_physician = fields.Boolean(compute="_compute_is_physician", store=True)

    is_physician = fields.Boolean(compute="_compute_is_physician", store=True)

    @api.depends("user_ids.groups_id")
    def _compute_is_physician(self):
        for rec in self:
            rec.is_physician = bool(
                rec.user_ids.filtered(
                    lambda user: user.has_group(
                        "pod_practice_management.group_podiatry_practice_physician"
                    )
                )
            )

    def write(self, vals):
        if (
            self.patient_ids
            and "name" in vals
            and not self._context.get("patient_update")
        ):
            raise ValidationError(
                _("To change a patient's name, change it from the patient form.")
            )
        return super().write(vals)

    @api.depends("practice_staff_rel_ids.practice_id")
    def _compute_practices_served(self):
        for rec in self:
            rec.practices_served_ids = rec.practice_staff_rel_ids.mapped("practice_id")

    @api.depends("practice_staff_rel_ids.practice_id")
    def _inverse_practices_served(self):
        for rec in self:
            for staff in rec.practice_staff_rel_ids:
                if staff.practice_id not in rec.practices_served_ids:
                    staff.unlink()
            served_practices = rec.practice_staff_rel_ids.mapped("practice_id")
            for practice in rec.practices_served_ids:
                if practice not in served_practices:
                    raise UserError(
                        _("To add a staff member to a practice, use the practice view.")
                    )
