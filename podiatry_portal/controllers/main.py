from odoo import http


class Main(http.Controller):

    @http.route("/podiatry/catalog", auth="public", website=True)
    def catalog(self, **kwargs):
        Prescription = http.request.env["podiatry.prescription"]
        prescriptions = Prescription.sudo().search([])
        res = http.request.render(
            "podiatry_portal.prescription_catalog",
            {"prescriptions": prescriptions},
        )
        return res
