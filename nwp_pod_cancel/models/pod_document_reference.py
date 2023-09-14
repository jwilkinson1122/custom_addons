from odoo import models


class PodiatryDocumentReference(models.Model):
    _inherit = "pod.document.reference"

    def check_cancellable(self):
        return True
