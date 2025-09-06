from odoo import fields, models


class ResConfigSetting(models.TransientModel):
    _inherit = "res.config.settings"

    brand_use_level = fields.Selection(
        string="Brand Use Level",
        related="company_id.brand_use_level",
        readonly=False,
    )
