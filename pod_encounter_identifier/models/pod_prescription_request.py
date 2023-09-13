from odoo import api, models


class PodiatryDeviceRequest(models.Model):
    _inherit = "pod.device.request"

    def _get_event_values(self):
        res = super()._get_event_values()
        if self.encounter_id:
            res["encounter_id"] = self.encounter_id.id
        return res

    @api.model
    def get_request_format(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pod.device.request.identifier")
        )

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
