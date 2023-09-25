# -*- coding: utf-8 -*-

from odoo import fields, models

class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Partner Types'

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
