from odoo import fields, models


class PodiatryCareplanCancel(models.TransientModel):
    _name = "pod.careplan.cancel"
    _description = "pod.careplan.cancel"
    _inherit = "pod.request.cancel"

    request_id = fields.Many2one("pod.careplan")
