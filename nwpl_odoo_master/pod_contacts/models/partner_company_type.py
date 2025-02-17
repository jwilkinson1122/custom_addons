# -*- coding: utf-8 -*-

from odoo import models, fields


class PartnerCompanyType(models.Model):
    _name = "partner.company.type"
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
