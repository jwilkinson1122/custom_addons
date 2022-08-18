
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_pod_administration_contact = fields.Boolean("Contact")
    module_pod_administration_contact_careplan = fields.Boolean(
        "Contact Care Plan"
    )
    module_pod_administration_location = fields.Boolean("Location")
    module_pod_administration_practitioner = fields.Boolean("Practitioner")
