# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartnerCompanyType(models.Model):
    _name = "res.partner.company.type"
    _description = "Company Types"

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
