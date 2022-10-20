from odoo import api, models


class PublisherReport(models.AbstractModel):
    _name = "report.pod_app.publisher_report"
    _description = "Publihser Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [("publisher_id", "in", docids)]
        items = self.env["pod.item"].search(domain)
        publishers = items.mapped("publisher_id")
        publisher_items = [
            (pub, items.filtered(lambda item: item.publisher_id == pub))
            for pub in publishers
        ]
        docargs = {
            "publisher_items": publisher_items,
        }
        return docargs
