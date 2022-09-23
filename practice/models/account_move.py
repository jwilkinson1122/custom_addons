# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get("prescription_id"):
            prescription = self.env["practice.prescription"].browse(
                self._context["prescription_id"])
            prescription.write(
                {"practice_invoice_id": res.id, "invoice_status": "invoiced"})
        return res
