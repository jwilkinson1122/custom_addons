from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_force_commercial_partner = fields.Boolean(
        string="Force commercial partner on invoices",
        help="When creating invoice from SO, always use commercial partner",
        config_parameter="invoice_force_commercial_partner",
        default=True,
    )
