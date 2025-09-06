import logging
from collections import defaultdict
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_amount = fields.Monetary(compute="_compute_client_credits_amount")

    def action_view_payments_in_favor(self):
        domain = self._payment_balance_customer_domain()
        domain.append(("balance", "<", 0.0))

        move_lines = (
            self.env["account.move.line"]
            .search(domain)
            .filtered(lambda line: self._account_move_line_has_residual(line))
        )

        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments"
        )
        action["domain"] = [("id", "in", move_lines.payment_id.ids)]
        return action
    
    def _compute_client_credits_amount(self):
        all_credits = defaultdict(float)
        domain = self._payment_balance_customer_domain()
        domain.append(("balance", "<", 0.0))

        for line in self.env["account.move.line"].search(domain):
            amount, is_zero = self._get_payment_amount_and_residual_zero(line)
            if is_zero:
                continue
            all_credits[line.partner_id.id] += amount

        for partner in self:
            partner.credit_amount = all_credits.get(partner.id, 0.0)


    # def _compute_client_credits_amount(self):
    #     for partner in self:
    #         partner.credit_amount = 0
    #         customer_credit = 0
    #         domain = self._payment_balance_customer_domain()
    #         domain.append(("balance", "<", 0.0))

    #         for line in self.env["account.move.line"].search(domain):
    #             amount, is_zero = self._get_payment_amount_and_residual_zero(line)
    #             if is_zero:
    #                 continue
    #             customer_credit += amount

    #         partner.credit_amount = customer_credit

    def _account_move_line_has_residual(self, line):
        _amount, is_zero = self._get_payment_amount_and_residual_zero(line)
        return not is_zero

    def _get_payment_amount_and_residual_zero(self, line):
        currency = self.env.company.currency_id
        if line.currency_id == self.env.company.currency_id:
            amount = abs(line.amount_residual_currency)
        else:
            amount = line.company_currency_id._convert(
                abs(line.amount_residual),
                currency,
                self.env.company,
                line.date,
            )
        return amount, currency.is_zero(amount)
    
    def _payment_balance_customer_domain(self):
    # Do not use ensure_one in a computed field
        return [
            ("account_id.account_type", "in", ("asset_receivable", "liability_payable")),
            ("parent_state", "=", "posted"),
            ("partner_id", "in", self.ids),
            ("reconciled", "=", False),
            "|",
            ("amount_residual", "!=", 0.0),
            ("amount_residual_currency", "!=", 0.0),
        ]


    # def _payment_balance_customer_domain(self):
    #     """Builds a domain for fetching customer balance-related account move lines."""
    #     self.ensure_one()
    #     return [
    #         (
    #             "account_id.account_type",
    #             "in",
    #             ("asset_receivable", "liability_payable"),
    #         ),
    #         ("parent_state", "=", "posted"),
    #         ("partner_id", "=", self.id),
    #         ("reconciled", "=", False),
    #         "|",
    #         ("amount_residual", "!=", 0.0),
    #         ("amount_residual_currency", "!=", 0.0),
    #     ]
