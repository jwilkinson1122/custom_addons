from odoo import http


class Prescriptions(http.Controller):

    @http.route("/podiatry/prescriptions")
    def list(self, **kwargs):
        Prescription = http.request.env["podiatry.prescription"]
        prescriptions = Prescription.search([])
        return http.request.render(
            "podiatry_app.prescription_list_template",
            {"prescriptions": prescriptions}
        )
