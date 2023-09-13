from odoo import fields, models

# FHIR Entity: Request (https://www.hl7.org/fhir/request.html)

class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"
    order_by_id = fields.Many2one(domain=[("is_requester", "=", True)])
