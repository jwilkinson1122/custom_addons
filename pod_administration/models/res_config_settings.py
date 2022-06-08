
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_administration_encounter = fields.Boolean("Encounter")
    module_pod_administration_encounter_careplan = fields.Boolean(
        "Encounter Care Plan"
    )
    module_pod_administration_location = fields.Boolean("Location")
    module_pod_administration_practitioner = fields.Boolean("Practitioner")
