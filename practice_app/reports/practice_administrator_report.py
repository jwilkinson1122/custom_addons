from odoo import api, models


class AdministratorReport(models.AbstractModel):
    _name = "report.practice_app.administrator_report"
    _description = "Publihser Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [("administrator_id", "in", docids)]
        prescriptions = self.env["practice.prescription"].search(domain)
        administrators = prescriptions.mapped("administrator_id")
        administrator_prescriptions = [
            (pub, prescriptions.filtered(
                lambda prescription: prescription.administrator_id == pub))
            for pub in administrators
        ]
        docargs = {
            "administrator_prescriptions": administrator_prescriptions,
        }
        return docargs
