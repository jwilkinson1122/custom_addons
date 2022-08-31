

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # module_podiatry_terminology_atc = fields.Boolean("ATC terminology")
    module_podiatry_terminology_sct = fields.Boolean("SCT terminology")
