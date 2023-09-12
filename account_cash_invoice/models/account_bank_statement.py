from odoo import models


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    def button_post(self):
        lines_of_moves_to_reconcile = self.line_ids.filtered(
            lambda line: line.move_id.state != "posted" and line.invoice_id
        )
        result = super(AccountBankStatement, self).button_post()
        for line in lines_of_moves_to_reconcile:
            (line.invoice_id.line_ids | line.move_id.line_ids).filtered(
                lambda l: l.account_internal_type in ("receivable", "payable")
            ).reconcile()
        return result
