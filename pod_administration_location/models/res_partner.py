
from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_location = fields.Boolean(default=False)
    location_identifier = fields.Char(readonly=True)
    description = fields.Text(string="Description")

    @api.model
    def _get_pod_identifiers(self):
        res = super(ResPartner, self)._get_pod_identifiers()
        res.append(
            (
                "is_pod",
                "is_location",
                "location_identifier",
                self._get_location_identifier,
            )
        )
        return res

    @api.model
    def _get_location_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.location") or "/"

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_location")
        return result
