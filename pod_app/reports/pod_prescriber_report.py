from odoo import api, models


class PrescriberReport(models.AbstractModel):
    _name = "report.pod_app.prescriber_report"
    _description = "Publihser Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [("prescriber_id", "in", docids)]
        prescriptions = self.env["pod.prescription"].search(domain)
        prescribers = prescriptions.mapped("prescriber_id")
        prescriber_prescriptions = [
            (pub, prescriptions.filtered(
                lambda prescription: prescription.prescriber_id == pub))
            for pub in prescribers
        ]
        docargs = {
            "prescriber_prescriptions": prescriber_prescriptions,
        }
        return docargs
