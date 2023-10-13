from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    account_invoice_storage_exchange_type_id = fields.Many2one("edi.exchange.type")
    account_invoice_storage_clean_file_name = fields.Boolean()
