

from odoo import models


class PodiatryEvent(models.AbstractModel):
    _name = "pod.event"
    _inherit = ["pod.event", "pod.commission.action"]
