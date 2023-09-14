

from odoo import fields, models


class ResUsersSignature(models.Model):
    _name = "res.users.signature"
    _description = "User Signature"

    user_id = fields.Many2one("res.users", required=True)
    signature = fields.Binary(required=True)
