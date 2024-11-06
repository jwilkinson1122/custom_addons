# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountAccount(models.Model):
    """inherited account account"""

    _inherit = "account.account"

    def _get_practice_domain(self):
        """method to get practice domain"""
        company = self.env.company
        practice_ids = self.env.user.practice_ids
        practice = practice_ids.filtered(
            lambda practice: practice.company_id == company
        )
        return [("id", "in", practice.ids)]

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        store=True,
        domain=_get_practice_domain,
        help="Leave this field empty if this account is"
        " shared between all practices",
    )
