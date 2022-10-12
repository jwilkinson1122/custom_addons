from odoo import http
from odoo.addons.podiatry_app.controllers.main import Prescriptions


class PrescriptionsExtended(Prescriptions):

    @http.route()
    def list(self, **kwargs):
        response = super().list(**kwargs)
        if kwargs.get("available"):
            all_prescriptions = response.qcontext["prescriptions"]
            available_prescriptions = all_prescriptions.filtered(
                "is_available")
            response.qcontext["prescriptions"] = available_prescriptions
        return response
