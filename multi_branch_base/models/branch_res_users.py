# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import UserError


class ResUsers(models.Model):
    """inherited res users"""

    _inherit = "res.users"

    branch_ids = fields.Many2many(
        "res.branch",
        string="Afilliate Branches",
        domain="[('partner_ids', 'in', partner_id)]",
        help="Branches this user is allowed to access.",
    )
    branch_id = fields.Many2one(
        "res.branch",
        string="Default Branch",
        domain="[('id', 'in', branch_ids)]",
        help="Default branch for the user.",
    )

    @api.constrains("branch_id")
    def _check_branch_id(self):
        """Ensure the selected branch is among the allowed branches."""
        for user in self:
            if user.branch_id and user.branch_id not in user.branch_ids:
                raise UserError(
                    _("The selected branch is not in the user's allowed branches.")
                )
