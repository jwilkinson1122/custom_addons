from odoo import http
from odoo.addons.pod_app.controllers.main import Patients


class PatientsExtended(Patients):

    @http.route()
    def list(self, **kwargs):
        response = super().list(**kwargs)
        if kwargs.get("available"):
            all_patients = response.qcontext["patients"]
            available_patients = all_patients.filtered("is_available")
            response.qcontext["patients"] = available_patients
        return response
