import logging

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
        for partner in self:
            partner.credit_amount = 0
            customer_credit = 0

            domain = self._payment_balance_customer_domain()

            domain.append(("balance", "<", 0.0))

            for line in self.env["account.move.line"].search(domain):

                amount, is_zero = self._get_payment_amount_and_residual_zero(line)

                if is_zero:
                    continue

                customer_credit += amount

            partner.credit_amount = customer_credit

    def _account_move_line_has_residual(self, line):
        _amount, is_zero = self._get_payment_amount_and_residual_zero(line)

        return not is_zero

    def _get_payment_amount_and_residual_zero(self, line):
        currency = self.env.company.currency_id
        if line.currency_id == self.env.company.currency_id:
            # Same foreign currency.
            amount = abs(line.amount_residual_currency)
        else:
            # Different foreign currencies.
            amount = line.company_currency_id._convert(
                abs(line.amount_residual),
                currency,
                self.env.company,
                line.date,
            )

        return amount, currency.is_zero(amount)

    def _payment_balance_customer_domain(self):
        self.ensure_one()

        domain = [
            (
                "account_id.account_type",
                "in",
                ("asset_receivable", "liability_payable"),
            ),
            ("parent_state", "=", "posted"),
            ("partner_id", "=", self.id),
            ("reconciled", "=", False),
            "|",
            ("amount_residual", "!=", 0.0),
            ("amount_residual_currency", "!=", 0.0),
        ]

        return domain

    def _compute_account_code(self, account_type):
        chart_code = (
            self.env["account.account"]
            .search([("account_type", "=", account_type)])
            .mapped("code")
        )
        account_code = max([eval(code) for code in chart_code]) + 1
        print(account_code)
        if str(account_code) in self.env["account.account"].search(
            [("id", "!=", False)]
        ).mapped("code"):
            arr = list(str(account_code))
            for i in range(1):
                arr.insert(5, "0")
            account_code = "".join(arr)
        return str(account_code)

    @api.model
    def create(self, vals):
        account_type = (
            "liability_payable"
            if "supplier_rank" in vals.keys()
            else "asset_receivable"
        )
        account_code = self._compute_account_code(account_type)

        account_id = self.env["account.account"].create(
            {"code": account_code, "name": vals["name"], "account_type": account_type}
        )

        if account_type == "liability_payable":
            vals["property_account_payable_id"] = account_id
        else:
            vals["property_account_receivable_id"] = account_id

        return super().create(vals)
