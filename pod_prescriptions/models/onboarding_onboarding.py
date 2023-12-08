

from odoo import api, models


class Onboarding(models.Model):
    _inherit = 'onboarding.onboarding'

    # Prescription Draft Rx Onboarding
    @api.model
    def action_close_panel_prescriptions_quotation(self):
        self.action_close_panel('pod_prescriptions.onboarding_onboarding_prescriptions_quotation')
