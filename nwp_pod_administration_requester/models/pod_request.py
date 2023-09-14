

from odoo import fields, models


class PodiatryRequest(models.AbstractModel):
    # FHIR Entity: Request (https://www.hl7.org/fhir/request.html)
    _inherit = "pod.request"
    order_by_id = fields.Many2one(domain=[("is_requester", "=", True)])
