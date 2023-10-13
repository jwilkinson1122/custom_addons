from odoo import models, api, fields


class ArchHeightType(models.Model):
    _name = "arch.height.type"

    name = fields.Char(required=True)
