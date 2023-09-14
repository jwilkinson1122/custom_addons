

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    delegated_agent_id = fields.Many2one("res.partner")
