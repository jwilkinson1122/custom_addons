from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_bank_reconciliation_start = fields.Date(
        related="company_id.account_bank_reconciliation_start", readonly=False
    )
