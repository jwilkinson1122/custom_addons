

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_podiatry_clinical_procedure = fields.Boolean("Procedures")
    module_podiatry_clinical_careplan = fields.Boolean("Care plans")
    module_podiatry_clinical_request_group = fields.Boolean("Request groups")
    module_podiatry_clinical_condition = fields.Boolean("Podiatry Condition")
