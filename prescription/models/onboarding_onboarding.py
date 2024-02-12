

from odoo import api, models


class Onboarding(models.Model):
    _inherit = 'onboarding.onboarding'

    # Prescription Draft Rx Onboarding
    @api.model
    def action_close_panel_prescription_quotation(self):
        self.action_close_panel('prescription.onboarding_onboarding_prescription_quotation')
