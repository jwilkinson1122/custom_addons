# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartnerContactPointTag(models.Model):
    _name = "res.partner.contact_point.tag"
    _inherit = "res.partner.contact_point.mixin"
    _description = "Contact Point Tag"

    name = fields.Char(translate=True)
