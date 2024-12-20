import base64
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_podiatry_calendar = fields.Boolean(string="Prescriptions for Patients")
    module_podiatry_encounter = fields.Boolean(string="Encounters for Patients")
    module_podiatry_patient_tags = fields.Boolean(string="Tags for Contacts")
    module_podiatry_phone_validation = fields.Boolean(
        string="Phone Number Validation for Contacts"
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "podiatry.module_podiatry_calendar",
            self.module_podiatry_calendar,
        )
        self.env["ir.config_parameter"].set_param(
            "podiatry.module_podiatry_encounter",
            self.module_podiatry_encounter,
        )
        self.env["ir.config_parameter"].set_param(
            "podiatry.module_podiatry_patient_tags",
            self.module_podiatry_patient_tags,
        )
        self.env["ir.config_parameter"].set_param(
            "podiatry.module_podiatry_phone_validation",
            self.module_podiatry_phone_validation,
        )
