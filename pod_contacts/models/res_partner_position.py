from odoo import fields, models


class ResPartnerPosition(models.Model):
    _name = "res.partner.position"
    _description = "Contact Positions"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
