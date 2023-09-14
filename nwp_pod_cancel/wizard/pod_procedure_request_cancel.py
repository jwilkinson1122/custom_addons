from odoo import fields, models


class PodiatryProcedureRequestCancel(models.TransientModel):
    _name = "pod.procedure.request.cancel"
    _inherit = "pod.request.cancel"
    _description = "pod.procedure.request.cancel"

    request_id = fields.Many2one("pod.procedure.request")
