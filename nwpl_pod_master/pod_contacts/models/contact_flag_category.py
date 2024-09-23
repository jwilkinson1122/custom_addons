from odoo import fields, models


class ContactFlag(models.Model):
    _name = "contact.flag.category"
    _description = "Contact Category Flag"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(required=True, default=True)
