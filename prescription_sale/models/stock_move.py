

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_return_prescription_vals(self, original_picking):
        res = super()._prepare_return_prescription_vals(original_picking)
        res.update(order_id=original_picking.sale_id.id)
        return res
