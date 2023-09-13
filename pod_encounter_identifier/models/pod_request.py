from odoo import models


class PodiatryRequest(models.AbstractModel):
    _name = "pod.request"
    _inherit = ["pod.request", "pod.identifier"]
