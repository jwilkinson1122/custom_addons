

from odoo import models


class PodiatryLaboratoryEvent(models.Model):
    _inherit = "pod.laboratory.event"

    def _change_authorization(self, vals, **kwargs):
        new_vals = {}
        for key in vals:
            if key in self._fields:
                new_vals[key] = vals[key]
        self.write(new_vals)
