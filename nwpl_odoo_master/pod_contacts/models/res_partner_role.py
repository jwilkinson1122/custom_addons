from odoo import fields, models


class ContactRole(models.Model):
    _name = "res.partner.role"
    _description = "Contact Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer(string="Color Index", default=0)
