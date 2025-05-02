from odoo import models


class ResPartner(models.Model):
    _inherit = ["res.partner", "attribute.set.owner.mixin"]
    _name = "res.partner"


class ResCountry(models.Model):
    _inherit = ["res.country", "attribute.set.owner.mixin"]
    _name = "res.country"
