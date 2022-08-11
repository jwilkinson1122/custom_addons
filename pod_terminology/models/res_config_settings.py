
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_terminology_code = fields.Boolean("Podiatry terminology")
