

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_podiatry_administration_practitioner_specialty = fields.Boolean(
        "Practitioner Specialty"
    )
