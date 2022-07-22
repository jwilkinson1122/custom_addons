from odoo import http


class Prescriptions(http.Controller):

    @http.route("/clinic/prescriptions")
    def list(self, **kwargs):
        Prescription = http.request.env["clinic.prescription"]
        prescriptions = Prescription.search([])
        return http.request.render(
            "clinic_app.prescription_list_template",
            {"prescriptions": prescriptions}
        )
