

from odoo import api, models


class PodiatryProcedureRequest(models.Model):
    _name = "pod.procedure.request"
    _inherit = ["pod.procedure.request", "pod.request"]

    @api.model
    def _pass_performer(self, activity, parent, plan, action):
        return True
