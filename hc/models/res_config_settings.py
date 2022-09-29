from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_hc_calendar = fields.Boolean(string="Appointments for Patients")
    module_hc_encounter = fields.Boolean(string="Encounters for Patients")
    module_hc_patient_tags = fields.Boolean(string="Tags for Patients")
    module_hc_phone_validation = fields.Boolean(string="Phone Number Validation for Patients")
