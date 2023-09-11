from odoo import models


class PodiatryPrescriptionAdministration(models.Model):
    _inherit = "pod.prescription.administration"

    def _get_procurement_group_vals(self):
        res = super()._get_procurement_group_vals()
        res["encounter_id"] = self.prescription_request_id.encounter_id.id
        return res
