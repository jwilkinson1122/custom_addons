from odoo import fields, models


class PodiatryEvent(models.AbstractModel):
    _name = "pod.event"
    _inherit = ["pod.event", "pod.nwp.identifier"]

    encounter_id = fields.Many2one("pod.encounter", readonly=True)
