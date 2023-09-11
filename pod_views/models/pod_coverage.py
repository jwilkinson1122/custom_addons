from odoo import api, models


class PodiatryCoverage(models.Model):
    _inherit = "pod.coverage"

    @api.depends("subscriber_id", "internal_identifier", "name")
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    rec.subscriber_id or rec.name or rec.internal_identifier,
                )
            )
        return result
