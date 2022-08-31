

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_podiatry_clinical = fields.Boolean("Clinical")
    module_podiatry_workflow = fields.Boolean("Workflow")
    module_podiatry_administration = fields.Boolean("Administration")
    module_podiatry_financial = fields.Boolean("Financial")
    module_podiatry_prescription = fields.Boolean("Prescription")
    module_podiatry_diagnostics = fields.Boolean("Diagnostics")
    module_podiatry_terminology = fields.Boolean("Terminologies")
