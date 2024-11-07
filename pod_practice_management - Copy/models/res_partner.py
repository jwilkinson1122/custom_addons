from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    child_practice_ids = fields.One2many(
        comodel_name="res.practice", inverse_name="parent_id"
    )
    contact_ids = fields.One2many(
        comodel_name="res.practice.contact", inverse_name="practice_id"
    )
    practice_contact_rel_ids = fields.One2many(
        comodel_name="res.practice.contact",
        inverse_name="partner_id",
        string="Employer(s)",
        help="The practices this person works for.",
    )
    practices_served_ids = fields.One2many(
        comodel_name="res.practice",
        compute="_compute_practices_served",
        inverse="_inverse_practices_served",
    )
    patient_ids = fields.One2many(comodel_name="res.patient", inverse_name="partner_id")

    is_manager = fields.Boolean(compute="_compute_is_manager", store=True)
    is_primary_physician = fields.Boolean(
        compute="_compute_is_primary_physician", store=True
    )

    is_manager = fields.Boolean(compute="_compute_is_manager", store=True)

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

    @api.depends("practice_contact_rel_ids.practice_id")
    def _compute_practices_served(self):
        for rec in self:
            rec.practices_served_ids = rec.practice_contact_rel_ids.mapped(
                "practice_id"
            )

    @api.depends("practice_contact_rel_ids.practice_id")
    def _inverse_practices_served(self):
        for rec in self:
            for contact in rec.practice_contact_rel_ids:
                if contact.practice_id not in rec.practices_served_ids:
                    contact.unlink()
            served_practices = rec.practice_contact_rel_ids.mapped("practice_id")
            for practice in rec.practices_served_ids:
                if practice not in served_practices:
                    raise UserError(
                        _(
                            "To add a contact member to a practice, use the practice view."
                        )
                    )
