from odoo import fields, models


class ResPartnerRole(models.Model):
    _name = "res.partner.role"
    _description = "Contact Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
