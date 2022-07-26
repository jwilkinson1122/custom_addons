
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_terminology_sct = fields.Boolean("SCT terminology")
