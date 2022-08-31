

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_podiatry_administration_encounter = fields.Boolean("Encounter")
    module_podiatry_administration_encounter_careplan = fields.Boolean(
        "Encounter-Careplan"
    )
    module_podiatry_administration_location = fields.Boolean("Location")
    module_podiatry_administration_practitioner = fields.Boolean(
        "Practitioner")
