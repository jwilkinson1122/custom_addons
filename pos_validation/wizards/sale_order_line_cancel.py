

from odoo import fields, models


class SaleOrderLineCancel(models.TransientModel):
    _name = "sale.order.line.cancel"
    _description = "sale.order.line.cancel"

    sale_order_line_id = fields.Many2one("sale.order.line", required=False)
    cancel_reason_id = fields.Many2one("pod.cancel.reason", required=True)

    def run(self):
        return self.sale_order_line_id.pod_cancel(self.cancel_reason_id)
