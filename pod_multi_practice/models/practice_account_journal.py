# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    """inherited account journal"""

    _inherit = "account.journal"

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
        domain=_get_practice_domain,
        help="Leave this field empty if this journal is"
        " shared between all practices",
    )

    default_account_id = fields.Many2one(
        comodel_name="account.account",
        check_company=True,
        copy=False,
        ondelete="restrict",
        string="Default Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id),"
        "'|', ('account_type', '=', default_account_type), "
        "('account_type', 'not in', ('asset_receivable', 'liability_payable')),"
        "'|',('practice_id', '=', practice_id), ('practice_id', '=', False)]",
    )

    suspense_account_id = fields.Many2one(
        comodel_name="account.account",
        check_company=True,
        ondelete="restrict",
        readonly=False,
        store=True,
        compute="_compute_suspense_account_id",
        help="Bank statements transactions will be posted on the suspense "
        "account until the final reconciliation "
        "allowing finding the right account.",
        string="Suspense Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), \
                        ('account_type', 'not in', ('asset_receivable', 'liability_payable')), \
                        ('account_type', '=', 'asset_current')], '|', "
        "('practice_id', '=', practice_id), ('practice_id', '=', False)",
    )

    profit_account_id = fields.Many2one(
        comodel_name="account.account",
        check_company=True,
        help="Used to register a profit when the ending balance of a cash "
        "register differs from what the system computes",
        string="Profit Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), \
                        ('account_type', 'not in', ('asset_receivable', 'liability_payable')), \
                        ('account_type', 'in', ('income', 'income_other')), '|', "
        "('practice_id', '=', practice_id), ('practice_id', '=', False)]",
    )

    loss_account_id = fields.Many2one(
        comodel_name="account.account",
        check_company=True,
        help="Used to register a loss when the ending balance of a cash "
        "register differs from what the system computes",
        string="Loss Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), \
                        ('account_type', 'not in', ('asset_receivable', 'liability_payable')), \
                        ('account_type', '=', 'expense'), '|', "
        "('practice_id', '=', practice_id), ('practice_id', '=', False)]",
    )

    # @api.onchange("practice_id")
    # def onchange_practice_id(self):
    #     """onchange method"""
    #     self.default_account_id = False
    #     self.suspense_account_id = False
    #     self.profit_account_id = False
    #     self.loss_account_id = False

    @api.onchange("practice_id")
    def onchange_practice_id(self):
        self.default_account_id = False
        self.suspense_account_id = False
        self.profit_account_id = False
        self.loss_account_id = False
        if self.practice_id:
            accounts = self.env["account.account"].search(
                [
                    "|",
                    ("practice_id", "=", self.practice_id.id),
                    ("practice_id", "=", False),
                ]
            )
        self.default_account_id = accounts and accounts[0] or False
