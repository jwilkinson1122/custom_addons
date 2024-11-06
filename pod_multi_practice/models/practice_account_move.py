# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    """inherited account move"""

    _inherit = "account.move"

    def _search_default_journal(self):
        if len(self.env.user.practice_ids) == 1:
            if self.is_sale_document(include_receipts=True):
                journal_types = ["sale"]
            elif self.is_purchase_document(include_receipts=True):
                journal_types = ["purchase"]
            elif self.payment_id or self.env.context.get("is_payment"):
                journal_types = ["bank", "cash"]
            else:
                journal_types = ["general"]
            practice_id = self.env.user.practice_id.id
            domain = [("practice_id", "=", practice_id), ("type", "in", journal_types)]
            journal = None
            currency_id = self.currency_id.id or self._context.get(
                "default_currency_id"
            )
            if currency_id and currency_id != self.company_id.currency_id.id:
                currency_domain = domain + [("currency_id", "=", currency_id)]
                journal = self.env["account.journal"].search(currency_domain, limit=1)

            if not journal:
                journal = self.env["account.journal"].search(domain, limit=1)
            if not journal:
                domain = [("type", "in", journal_types), ("practice_id", "=", False)]
                journal = self.env["account.journal"].search(domain, limit=1)
            if not journal:
                practice = self.env.user.practice_id

                error_msg = _(
                    "No journal could be found in practice %(practice_name)s for any of those types: %(journal_types)s",
                    practice_name=practice.name,
                    journal_types=", ".join(journal_types),
                )
                raise UserError(error_msg)
        else:
            journal = super(AccountMove, self)._search_default_journal()
            return journal

    def _get_default_practice(self):
        if len(self.env.user.practice_ids) == 1:
            practice = self.env.user.practice_id
            return practice
        return False

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
        readonly=False,
        default=_get_default_practice,
        domain=_get_practice_domain,
    )

    @api.onchange("practice_id")
    def onchange_practice_id(self):
        """onchange method"""
        move_type = self._context.get("default_move_type", "entry")
        if move_type in self.get_sale_types(include_receipts=True):
            journal_types = ["sale"]
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_types = ["purchase"]
        else:
            journal_types = self._context.get("default_move_journal_types", ["general"])
        practice_id = self.practice_id.id
        domain = [("practice_id", "=", practice_id), ("type", "in", journal_types)]
        journal = None
        if self._context.get("default_currency_id"):
            currency_domain = domain + [
                ("currency_id", "=", self._context["default_currency_id"])
            ]
            journal = self.env["account.journal"].search(currency_domain, limit=1)
        if not journal:
            journal = self.env["account.journal"].search(domain, limit=1)
        if not journal:
            domain = [("type", "in", journal_types), ("practice_id", "=", False)]
            journal = self.env["account.journal"].search(domain, limit=1)
        if not journal and journal_types:
            practice = self.practice_id
            error_msg = _(
                "No journal could be found in %(practice)s practice for "
                "any of those types: %(journal_types)s",
                practice=practice.name,
                journal_types=", ".join(journal_types),
            )
            raise UserError(error_msg)
        self.journal_id = journal

    @api.depends("company_id", "invoice_filter_type_domain")
    def _compute_suitable_journal_ids(self):
        """method to compute suitable journal ids"""
        if self.practice_id:
            for m in self:
                journal_type = m.invoice_filter_type_domain or "general"
                practice_id = m.practice_id.id  # or self.env.user.practice_id.id
                domain = [
                    ("type", "=", journal_type),
                    "|",
                    ("practice_id", "=", practice_id),
                    ("practice_id", "=", False),
                ]
                m.suitable_journal_ids = self.env["account.journal"].search(domain)

        else:
            return super(AccountMove, self)._compute_suitable_journal_ids()

    @api.constrains("practice_id", "line_ids")
    def _check_move_line_practice_id(self):
        """method to check practice of accounts and entry"""
        for move in self:
            practices = move.line_ids.account_id.practice_id
            if practices and practices != move.practice_id:
                bad_accounts = move.line_ids.account_id.filtered(
                    lambda a: a.practice_id and a.practice_id != move.practice_id
                )
                raise ValidationError(
                    _(
                        "Your items contains accounts from %(line_practice)s practice"
                        " whereas your entry belongs to %(move_practice)s practice. "
                        "\n Please change the practice of your entry or remove the "
                        "accounts from other practices (%(bad_accounts)s).",
                        line_practice=", ".join(practices.mapped("name")),
                        move_practice=move.practice_id.name,
                        bad_accounts=", ".join(bad_accounts.mapped("name")),
                    )
                )


class AccountMoveLine(models.Model):
    """inherited account move line"""

    _inherit = "account.move.line"

    practice_id = fields.Many2one(
        "res.practice", related="move_id.practice_id", string="Practice", store=True
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
        compute="_compute_account_id",
        store=True,
        readonly=False,
        precompute=True,
        inverse="_inverse_account_id",
        index=True,
        ondelete="cascade",
        domain="[('deprecated', '=', False), "
        "('company_id', '=', company_id), '|', "
        "('practice_id', '=', practice_id), ('practice_id', '=', False)]",
        check_company=True,
        tracking=True,
    )
