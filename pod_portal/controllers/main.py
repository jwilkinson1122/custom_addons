from odoo import http


class Main(http.Controller):

    @http.route("/pod/catalog", auth="public", website=True)
    def catalog(self, **kwargs):
        Patient = http.request.env["pod.patient"]
        patients = Patient.sudo().search([])
        res = http.request.render(
            "pod_portal.patient_catalog",
            {"patients": patients},
        )
        return res
