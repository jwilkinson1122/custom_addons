from odoo import http


class Main(http.Controller):

    @http.route("/pod/archive", auth="public", website=True)
    def archive(self, **kwargs):
        Prescription = http.request.env["pod.prescription"]
        prescriptions = Prescription.sudo().search([])
        res = http.request.render(
            "pod_portal.prescription_archive",
            {"prescriptions": prescriptions},
        )
        return res
