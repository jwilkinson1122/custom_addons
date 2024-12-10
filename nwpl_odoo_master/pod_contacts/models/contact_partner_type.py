# -*- coding: utf-8 -*-

from odoo import models, fields


class ContactPartnerType(models.Model):
    _name = "contact.partner.type"
    _description = "Partner Types"

    name = fields.Char(
        required=True,
    )

    description = fields.Char(
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )
