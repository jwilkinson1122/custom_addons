# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    """inherited account payment"""

    _inherit = "account.payment"

    destination_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Destination Account",
        store=True,
        readonly=False,
        compute="_compute_destination_account_id",
        domain="[('account_type', 'in', ('asset_receivable', 'liability_payable')), ('company_id', '=', company_id), "
        "'|', ('practice_id', '=', practice_id), ('practice_id', '=', False)]",
        check_company=True,
    )

    @api.constrains("practice_id")
    def _check_payment_practice_id(self):
        """method to check practice of accounts and entry"""
        for payment in self:
            practice = payment.destination_account_id.practice_id
            if practice and practice != payment.practice_id:
                raise ValidationError(
                    _(
                        "Your payment belongs to  '%s' practice whereas the account"
                        " belongs to '%s' practice.",
                        payment.practice_id.name,
                        practice.name,
                    )
                )

    @api.depends(
        "journal_id",
        "practice_id",
        "partner_id",
        "partner_type",
        "is_internal_transfer",
        "destination_journal_id",
    )
    def _compute_destination_account_id(self):
        """method to compute destination account"""
        if self.practice_id:
            self.destination_account_id = False
            for pay in self:
                if pay.is_internal_transfer:
                    pay.destination_account_id = (
                        pay.journal_id.company_id.transfer_account_id
                    )
                elif pay.partner_type == "customer":
                    # Receive money from invoice or send money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id
                        ).property_account_receivable_id
                    else:
                        destination_account = self.env["account.account"].search(
                            [
                                ("company_id", "=", pay.company_id.id),
                                ("practice_id", "=", pay.practice_id.id),
                                ("internal_type", "=", "receivable"),
                            ],
                            limit=1,
                        )
                        pay.destination_account_id = destination_account
                        if not destination_account:
                            destination_account = self.env["account.account"].search(
                                [
                                    ("company_id", "=", pay.company_id.id),
                                    ("practice_id", "=", False),
                                    ("internal_type", "=", "receivable"),
                                ],
                                limit=1,
                            )
                        pay.destination_account_id = destination_account
                elif pay.partner_type == "supplier":
                    # Send money to pay a bill or receive money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id
                        ).property_account_payable_id
                    else:
                        destination_account = self.env["account.account"].search(
                            [
                                ("company_id", "=", pay.company_id.id),
                                ("practice_id", "=", pay.practice_id.id),
                                ("internal_type", "=", "payable"),
                            ],
                            limit=1,
                        )
                        pay.destination_account_id = destination_account
                        if not destination_account:
                            destination_account = self.env["account.account"].search(
                                [
                                    ("company_id", "=", pay.company_id.id),
                                    ("practice_id", "=", False),
                                    ("internal_type", "=", "payable"),
                                ],
                                limit=1,
                            )
                            pay.destination_account_id = destination_account
        else:
            res = super(AccountPayment, self)._compute_destination_account_id()
            return res
