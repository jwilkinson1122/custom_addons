from odoo import api, models


class AdministratorReport(models.AbstractModel):
    _name = "report.clinic_app.administrator_report"
    _description = "Administrator Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [("administrator_id", "in", docids)]
        prescriptions = self.env["clinic.prescription"].search(domain)
        administrators = prescriptions.mapped("administrator_id")
        administrator_prescriptions = [
            (admin, prescriptions.filtered(
                lambda prescription: prescription.administrator_id == admin))
            for admin in administrators
        ]
        docargs = {
            "administrator_prescriptions": administrator_prescriptions,
        }
        return docargs
