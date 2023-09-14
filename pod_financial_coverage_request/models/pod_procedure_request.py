# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PodiatryProcedureRequest(models.Model):
    _name = "pod.procedure.request"
    _inherit = ["pod.procedure.request", "pod.request"]

    @api.model
    def _pass_performer(self, activity, parent, plan, action):
        return True
