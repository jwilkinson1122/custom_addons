from odoo import api, models


class PodiatryCareplan(models.Model):
    _inherit = "pod.careplan"

    @api.model
    def get_request_format(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pod.careplan.identifier")
        )

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_nwp_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
