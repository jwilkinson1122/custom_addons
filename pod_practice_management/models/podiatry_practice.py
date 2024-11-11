from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError


class PodiatryPractice(models.Model):
    _name = "podiatry.practice"
    _description = "Podiatry Practice"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    patient_ids = fields.Many2many(
        comodel_name="podiatry.patient",
        relation="podiatry_practice_patient_rel",
        column1="practice_id",
        column2="patient_id",
        string="Patients",
        tracking=True,
    )
    patient_count = fields.Integer(compute="_compute_patient_counts")
    inactive_count = fields.Integer(compute="_compute_patient_counts")
    active_count = fields.Integer(compute="_compute_patient_counts")
    parent_id = fields.Many2one(
        comodel_name="res.partner",
        string="Parent Account",
        ondelete="restrict",
        tracking=True,
    )
    # contact_ids = fields.One2many(
    #     domain=[("active", "=", True), ("is_company", "=", False)]
    # )

    contact_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="parent_id",
        domain=[("is_company", "=", False)],
        tracking=True,
    )

    staff_ids = fields.One2many(
        comodel_name="podiatry.practice.staff",
        inverse_name="practice_id",
        tracking=True,
    )
    manager_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_manager",
        store=True,
    )
    manager_name = fields.Char(
        related="manager_id.name",
        string="Practice Manager Name",
    )
    physician_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_physician",
        store=True,
        string="Primary Physician",
    )
    physician_name = fields.Char(
        related="physician_id.name",
        string="Primary Physician Name",
    )
    website = fields.Char()

    allowed_user_ids = fields.Many2many(
        comodel_name="res.users",
        compute="_compute_allowed_user_ids",
        inverse="_inverse_allowed_user_ids",
    )

    def write(self, vals):
        previous_patient_ids = self.sudo().patient_ids
        res = super().write(vals)
        if "staff_ids" in vals or "patient_ids" in vals:
            (self.sudo().patient_ids | previous_patient_ids).recompute_followers()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for index, rec in enumerate(res):
            if "staff_ids" in vals_list[index]:
                rec.sudo().patient_ids.recompute_followers()
        return res

    def unlink(self):
        to_recompute = self.patient_ids
        res = super().unlink()
        to_recompute.recompute_followers()
        return res

    @api.depends("patient_ids.is_active")
    def _compute_patient_counts(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)
            rec.inactive_count = len(rec.patient_ids.filtered(lambda p: p.is_active))
            rec.active_count = rec.patient_count - rec.inactive_count

    @api.depends("staff_ids.role")
    def _compute_manager(self):
        for rec in self:
            staff = rec.staff_ids.filtered(lambda r: r.role == "manager")
            rec.manager_id = staff.partner_id if staff else False

    @api.depends("staff_ids.role")
    def _compute_physician(self):
        for rec in self:
            staff = rec.staff_ids.filtered(lambda r: r.role == "physician")
            rec.physician_id = staff.partner_id if staff else False

    def _compute_allowed_user_ids(self):
        for rec in self:
            rec.allowed_user_ids = rec.staff_ids.user_ids

    def _inverse_allowed_user_ids(self):
        for rec in self:
            removed_staff = rec.staff_ids.filtered(
                lambda staff: staff.user_ids not in rec.allowed_user_ids
            )
            added_users = rec.allowed_user_ids - rec.staff_ids.user_ids
            removed_staff.unlink()
            self.env["podiatry.practice.staff"].create(
                [
                    {
                        "practice_id": rec.id,
                        "partner_id": user.partner_id.id,
                        "role": "other",
                    }
                    for user in added_users
                ]
            )

    def remove_access(self, user):
        self.staff_ids.filtered(lambda staff: user in staff.user_ids).unlink()


class PracticeStaff(models.Model):
    _name = "podiatry.practice.staff"
    _description = "Podiatry Practice Staff"

    sequence = fields.Integer()
    practice_id = fields.Many2one(
        comodel_name="podiatry.practice",
        string="Practice",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contacts",
        required=True,
        domain=[("is_company", "=", False)],
        ondelete="cascade",
    )
    active = fields.Boolean(related="partner_id.active")
    role = fields.Selection(
        selection=[
            ("manager", "Practice Manager"),  # Only One
            ("physician", "Primary Physician"),  # One or more
            ("assistant", "Assistant"),  # One or more
            ("physician", "Physician"),  # One or more
            ("orthotist", "Orthotist"),  # One or more
            ("therapist", "Physical Therapist"),  # One or more
            ("nurse", "Nurse"),  # One or more
            ("receptionist", "Receptionist"),  # One or more
            ("administrative", "Administrative"),  # One or more
            ("other", "Other"),
        ],
        required=True,
    )

    mobile = fields.Char(related="partner_id.mobile", readonly=False)
    name = fields.Char(related="partner_id.name", readonly=False)
    parent_id = fields.Many2one(
        related="partner_id.parent_id",
        readonly=False,
        string="Account",
        domain=[("is_company", "=", True)],
    )
    email = fields.Char(related="partner_id.email", readonly=False)
    user_ids = fields.One2many(related="partner_id.user_ids", readonly=True)
    has_portal_access = fields.Boolean(
        compute="_compute_has_portal_access", compute_sudo=True
    )

    _sql_constraints = [
        (
            "practice_staff_unique",
            "unique(practice_id, partner_id)",
            "Each partner can only be related to a given practice once.",
        )
    ]

    # @api.constrains("role")
    # def _constrain_role(self):
    #     practices = self.mapped("practice_id")
    #     for practice in practices:
    #         if (
    #             len(practice.staff_ids.filtered(lambda r: r.role == "manager"))
    #             > 1
    #         ):
    #             raise ValidationError(
    #                 _("A practice can have only one practice assistant.")
    #             )
    #         if (
    #             len(
    #                 practice.staff_ids.filtered(lambda r: r.role == "physician")
    #             )
    #             > 1
    #         ):
    #             raise ValidationError(
    #                 _("A practice can have only one primary physician.")
    #             )

    @api.constrains("role")
    def _constrain_role(self):
        # Define roles that should only have one instance per practice
        unique_roles = {
            "manager": "Practice Manager",
            # "physician": "Primary Physician"
        }

        practices = self.mapped("practice_id")
        for practice in practices:
            for role_key, role_name in unique_roles.items():
                role_count = len(
                    practice.staff_ids.filtered(lambda r: r.role == role_key)
                )
                if role_count > 1:
                    raise ValidationError(
                        _("A practice can have only one %s.") % role_name
                    )

    @api.onchange("mobile")
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self.partner_id._phone_format(
                self.mobile, force_format="INTERNATIONAL"
            )

    @api.depends("user_ids", "user_ids.groups_id")
    def _compute_has_portal_access(self):
        for rec in self:
            rec.has_portal_access = (
                bool(rec.user_ids.filtered(lambda r: r.has_group("base.group_portal")))
                or bool(rec.user_ids.filtered(lambda r: r.has_group("base.group_user")))
                or bool(rec.partner_id.signup_token)
            )

    def action_revoke_portal_access(self):
        group_portal = self.env.ref("base.group_portal")
        group_public = self.env.ref("base.group_public")
        self.user_ids.write(
            {
                "groups_id": [
                    Command.unlink(group_portal.id),
                    Command.link(group_public.id),
                ],
                "active": False,
            }
        )
        # Remove the signup token, so it cannot be used
        self.partner_id.sudo().signup_token = False

    def action_grant_portal_access(self):
        wiz = self.env["portal.wizard"].create(
            {"partner_ids": [(4, self.partner_id.id)]}
        )
        return wiz._action_open_modal()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.practice_id.mapped("patient_ids").recompute_followers()
        return res

    def unlink(self):
        patients = self.practice_id.mapped("patient_ids")
        res = super().unlink()
        patients.recompute_followers()
        return res

    def write(self, values):
        if "practice_id" in values:
            to_recompute = self.env["podiatry.patient"]
            for rec in self:
                if rec.practice_id.id != values["practice_id"]:
                    to_recompute |= rec.practice_id.patient_ids
            res = super().write(values)
            to_recompute.recompute_followers()
            return res
        return super().write(values)
