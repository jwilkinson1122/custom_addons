from odoo import http


class Main(http.Controller):

    @http.route("/clinic/archive", auth="adminlic", website=True)
    def archive(self, **kwargs):
        Prescription = http.request.env["clinic.prescription"]
        prescriptions = Prescription.sudo().search([])
        res = http.request.render(
            "clinic_portal.prescription_archive",
            {"prescriptions": prescriptions},
        )
        return res
