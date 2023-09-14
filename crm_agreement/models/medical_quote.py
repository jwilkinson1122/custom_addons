from odoo import fields, models


class PodiatryQuote(models.Model):

    _inherit = "pod.quote"

    lead_id = fields.Many2one("crm.lead")
