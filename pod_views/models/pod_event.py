from odoo import api, models


class PodiatryEvent(models.AbstractModel):
    _inherit = "pod.event"

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.internal_identifier))
        return result
