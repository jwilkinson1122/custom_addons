from odoo import fields, models


class ContactRole(models.Model):
    _name = "contact.role"
    _description = "Contact Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
