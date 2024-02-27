from odoo import models


class POSSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        res["search_params"]["fields"].append("ref")
        return res
