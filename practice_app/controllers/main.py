from odoo import http


class Prescriptions(http.Controller):

    @http.route("/practice/prescriptions")
    def list(self, **kwargs):
        Prescription = http.request.env["practice.prescription"]
        prescriptions = Prescription.search([])
        return http.request.render(
            "practice_app.prescription_list_template",
            {"prescriptions": prescriptions}
        )
