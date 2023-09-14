

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def demo_history_back(self):
        return {"type": "ir.actions.client", "tag": "history_back"}
