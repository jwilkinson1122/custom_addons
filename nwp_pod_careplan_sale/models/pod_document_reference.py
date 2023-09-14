from odoo import models


class PodiatryDocumentReference(models.Model):
    _inherit = "pod.document.reference"

    def check_is_billable(self):
        return self.is_billable
