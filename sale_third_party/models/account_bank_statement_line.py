from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    third_party_sale_order_id = fields.Many2one(
        "sale.order", string="third party sale order", readonly=True
    )
