from odoo import fields, models


class ResPartnerFlagCategory(models.Model):
    _name = "res.partner.flag.category"
    _description = "Partner Category Flag"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(required=True, default=True)
