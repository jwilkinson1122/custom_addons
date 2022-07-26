
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_clinical_procedure = fields.Boolean("Procedures")
    module_pod_clinical_careplan = fields.Boolean("Care plans")
    module_pod_clinical_request_group = fields.Boolean("Request groups")
    module_pod_clinical_condition = fields.Boolean("Pathology")
