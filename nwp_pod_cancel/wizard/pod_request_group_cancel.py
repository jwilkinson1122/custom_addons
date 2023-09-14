from odoo import fields, models


class PodiatryRequestGroupCancel(models.TransientModel):
    _name = "pod.request.group.cancel"
    _inherit = "pod.request.cancel"
    _description = "pod.request.group.cancel"

    request_id = fields.Many2one("pod.request.group")
