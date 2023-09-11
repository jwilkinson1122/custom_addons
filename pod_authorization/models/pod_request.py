from odoo import fields, models


class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"

    authorization_checked = fields.Boolean(default=False, readonly=True)
