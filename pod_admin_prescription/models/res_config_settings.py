

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_podiatry_prescription_request = fields.Boolean(
        "Prescription Request")
