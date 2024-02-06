# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get("prescription_order_id"):
            prescription = self.env["prescription.order"].browse(self._context["prescription_order_id"])
            prescription.write({"prescription_invoice_id": res.id, "invoice_status": "invoiced"})
        return res
