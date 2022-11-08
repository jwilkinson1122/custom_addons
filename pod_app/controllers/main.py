from odoo import http


class Patients(http.Controller):

    @http.route("/pod/patients")
    def list(self, **kwargs):
        Patient = http.request.env["pod.patient"]
        patients = Patient.search([])
        return http.request.render(
            "pod_app.patient_list_template",
            {"patients": patients}
        )
