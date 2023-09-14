

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    payment_responsible_id = fields.Many2one("res.users")
