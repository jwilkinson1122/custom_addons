from odoo import fields, models


class PodiatryLaboratoryRequestCancel(models.TransientModel):
    _name = "pod.laboratory.request.cancel"
    _inherit = "pod.request.cancel"
    _description = "pod.laboratory.request.cancel"

    request_id = fields.Many2one("pod.laboratory.request")
