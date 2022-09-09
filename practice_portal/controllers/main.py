from odoo import http


class Main(http.Controller):

    @http.route("/practice/catalog", auth="public", website=True)
    def catalog(self, **kwargs):
        Prescription = http.request.env["practice.prescription"]
        prescriptions = Prescription.sudo().search([])
        res = http.request.render(
            "practice_portal.prescription_catalog",
            {"prescriptions": prescriptions},
        )
        return res
