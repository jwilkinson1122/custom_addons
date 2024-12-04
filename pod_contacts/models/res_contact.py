from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResContact(models.Model):
    _name = "res.contact"
    _inherits = {"res.partner": "partner_id"}

    is_company_parent = fields.Boolean(default=False)
    is_contact = fields.Boolean(default=False)
    is_patient = fields.Boolean(default=False)

    create_users_button = fields.Boolean(
        compute="_compute_create_users_button",
        store=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Provider Contact",
        index=True,
        tracking=True,
        required=True,
        help="Link to the partner record.",
    )

    related_user_id = fields.Many2one(
        related="partner_id.user_id",
        string="Related User",
        readonly=True,
    )

    @api.depends("partner_id.user_ids")
    def _compute_create_users_button(self):
        """Compute the visibility of the 'Create Portal User' button."""
        for record in self:
            record.create_users_button = not bool(record.partner_id.user_ids)
