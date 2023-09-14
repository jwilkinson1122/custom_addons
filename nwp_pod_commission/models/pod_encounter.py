

from odoo import models


class PodiatryEncounter(models.AbstractModel):
    _inherit = "pod.encounter"

    def recompute_commissions(self):
        for rec in self:
            rec._compute_commissions()
        return True

    def create_sale_order(self):
        res = super().create_sale_order()
        self._compute_commissions()
        return res

    def _compute_commissions(self):
        self.ensure_one()
        for pr in self.careplan_ids.mapped("procedure_request_ids"):
            for procedure in pr.procedure_ids:
                procedure.compute_commission(pr)
        for request in self.careplan_ids.mapped("laboratory_request_ids"):
            request.compute_commission(request)
        for event in self.careplan_ids.mapped("laboratory_request_ids").mapped(
            "laboratory_event_ids"
        ):
            event.compute_commission()
