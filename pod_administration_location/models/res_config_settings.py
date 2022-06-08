
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_administration_location_stock = fields.Boolean(
        "Stock Location"
    )
