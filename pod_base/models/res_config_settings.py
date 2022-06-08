
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_clinical = fields.Boolean("Clinical")
    module_pod_workflow = fields.Boolean("Workflow")
    module_pod_administration = fields.Boolean("Administration")
    module_pod_financial = fields.Boolean("Financial")
    module_pod_prescription = fields.Boolean("Prescription")
    module_pod_diagnostics = fields.Boolean("Diagnostics")
    module_pod_terminology = fields.Boolean("Terminologies")
