

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def recompute_lines_agents(self):
        # Commission on pod sale orders will not be managed by the
        # recompute function
        return super(
            SaleOrder, self.filtered(lambda r: not r.encounter_id)
        ).recompute_lines_agents()
