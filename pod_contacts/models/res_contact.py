from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResContact(models.Model):
    _name = "res.contact"
    _inherits = {"res.partner": "partner_id"}

    is_contact = fields.Boolean(default=False)
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
        """Compute the visibility of the 'Create User' button."""
        for record in self:
            record.create_users_button = not bool(record.partner_id.user_ids)

    def create_contacts(self):
        """Create user for res.contact."""
        self.ensure_one()
        if self.partner_id.user_ids:
            raise UserError(_("A user for this contact already exists."))

        # Add groups
        contact_group = self.env.ref("base.group_contact_user")
        internal_user_group = self.env.ref("base.group_user")
        group_ids = [contact_group.id, internal_user_group.id]

        return {
            "type": "ir.actions.act_window",
            "name": _("Create Login"),
            "view_mode": "form",
            "view_id": self.env.ref("pod_contacts.view_create_user_wizard_form").id,
            "target": "new",
            "res_model": "res.users",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_groups_id": [(6, 0, group_ids)],
            },
        }

    # def create_contacts(self):
    #     """Action to create a user for the contact."""
    #     self.ensure_one()

    #     if self.partner_id.user_ids:
    #         raise UserError(_("A user for this contact already exists."))

    #     contact_group = self.env.ref("base.group_contact_user")
    #     internal_user_group = self.env.ref("base.group_user")
    #     group_ids = [contact_group.id, internal_user_group.id]

    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": _("Create Login"),
    #         "view_mode": "form",
    #         "view_id": self.env.ref("pod_contacts.view_create_user_wizard_form").id,
    #         "target": "new",
    #         "res_model": "res.users",
    #         "context": {
    #             "default_partner_id": self.partner_id.id,
    #             "default_groups_id": [(6, 0, group_ids)],
    #         },
    #     }
