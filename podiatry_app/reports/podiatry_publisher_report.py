from odoo import api, models


class PublisherReport(models.AbstractModel):
    _name = "report.podiatry_app.publisher_report"
    _description = "Publihser Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [("publisher_id", "in", docids)]
        prescriptions = self.env["podiatry.prescription"].search(domain)
        publishers = prescriptions.mapped("publisher_id")
        publisher_prescriptions = [
            (pub, prescriptions.filtered(
                lambda prescription: prescription.publisher_id == pub))
            for pub in publishers
        ]
        docargs = {
            "publisher_prescriptions": publisher_prescriptions,
        }
        return docargs
