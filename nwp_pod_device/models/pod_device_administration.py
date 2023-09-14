from odoo import models


class PodiatryDeviceAdministration(models.Model):
    _inherit = "pod.device.administration"

    def _get_procurement_group_vals(self):
        res = super()._get_procurement_group_vals()
        res["encounter_id"] = self.device_request_id.encounter_id.id
        return res
