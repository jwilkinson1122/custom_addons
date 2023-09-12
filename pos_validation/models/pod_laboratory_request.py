from odoo import models


class PodiatryLaboratoryRequest(models.Model):
    _name = "pod.laboratory.request"
    _inherit = ["pod.laboratory.request", "pod.request"]

    def _check_cancellable(self):
        if self.mapped("laboratory_event_ids").filtered(
            lambda r: r.fhir_state != "aborted"
        ):
            return False
        return super()._check_cancellable()
