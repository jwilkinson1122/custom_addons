from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    email_integration_password = fields.Char(readonly=True)
