

from odoo import models


class LaboratoryRequest(models.Model):
    _inherit = "pod.laboratory.request"

    def get_sale_order_query(self):
        query = super().get_sale_order_query()
        query += self.mapped("laboratory_event_ids").get_sale_order_query()
        return query

    def _get_event_values(self, vals=False):
        res = super()._get_event_values(vals)
        res["encounter_id"] = self.encounter_id.id or False
        if not res.get("authorization_status", False):
            res["authorization_status"] = self.authorization_status
        cai = self.env["pod.coverage.agreement.item"].get_item(
            self.service_id,
            self.coverage_id.coverage_template_id,
            self.center_id,
        )
        if cai:
            res["coverage_agreement_id"] = cai.coverage_agreement_id.id
        return res
