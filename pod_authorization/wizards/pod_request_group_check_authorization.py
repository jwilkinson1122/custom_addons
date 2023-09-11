from odoo import api, fields, models


class PodiatryRequestGroupCheckAuthorization(models.TransientModel):
    _inherit = "pod.request.group.check.authorization"

    @api.model
    def _default_authorization(self):
        return self._default_request().authorization_checked

    authorization_checked = fields.Boolean(default=_default_authorization)

    def _get_kwargs(self):
        res = super()._get_kwargs()
        res["authorization_checked"] = self.authorization_checked
        return res
