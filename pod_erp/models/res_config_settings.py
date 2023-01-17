from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # module_podiatry_product_configurator = fields.Boolean(
    #     string="Product Configurator for custom devices")

    module_pod_calendar = fields.Boolean(
        string="Prescriptions for Patients")
    module_pod_encounter = fields.Boolean(
        string="Encounters for Patients")
    # module_podiatry_product = fields.Boolean(
    #     string="Product Configuration")
    module_pod_patient_tags = fields.Boolean(string="Tags for Patients")
    module_pod_phone_validation = fields.Boolean(
        string="Phone Number Validation for Patients")
