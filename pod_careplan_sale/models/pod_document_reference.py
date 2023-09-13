from odoo import models


class PodiatryDocumentReference(models.Model):
    _inherit = "pod.document.reference"

    def check_is_billable(self):
        retursn self.is_billable
