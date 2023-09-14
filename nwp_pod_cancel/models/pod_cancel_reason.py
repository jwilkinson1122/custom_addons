from odoo import fields, models


class PodiatryCancelReason(models.Model):
    _name = "pod.cancel.reason"
    _description = "Cancellation reason"

    name = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(required=True, default=True)
