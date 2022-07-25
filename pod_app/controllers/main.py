from odoo import http


class Prescriptions(http.Controller):

    @http.route("/pod/prescriptions")
    def list(self, **kwargs):
        Prescription = http.request.env["pod.prescription"]
        prescriptions = Prescription.search([])
        return http.request.render(
            "pod_app.prescription_list_template",
            {"prescriptions": prescriptions}
        )
