from odoo import fields, models


class PodiatryCareplanCancel(models.AbstractModel):
    _name = "pod.request.cancel"
    _description = "pod.request.cancel"

    request_id = fields.Many2one("pod.request", required=True, readonly=True)
    cancel_reason_id = fields.Many2one("pod.cancel.reason", required=True)
    cancel_reason = fields.Text(string="Description")

    def run(self):
        self.ensure_one()
        self.request_id.with_context(
            cancel_reason_id=self.cancel_reason_id.id,
            cancel_reason=self.cancel_reason,
        ).cancel()
