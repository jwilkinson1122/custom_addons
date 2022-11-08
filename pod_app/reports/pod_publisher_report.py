from odoo import api, models


class PublisherReport(models.AbstractModel):
    _name = "report.pod_app.publisher_report"
    _description = "Publihser Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [("publisher_id", "in", docids)]
        patients = self.env["pod.patient"].search(domain)
        publishers = patients.mapped("publisher_id")
        publisher_patients = [
            (pub, patients.filtered(lambda patient: patient.publisher_id == pub))
            for pub in publishers
        ]
        docargs = {
            "publisher_patients": publisher_patients,
        }
        return docargs
