from odoo import models, api, fields


class TopcoverType(models.Model):
    _name = "topcover.type"

    name = fields.Char(required=True)


class TopcoverStyle(models.Model):
    _name = "topcover.style"

    name = fields.Char(required=True)


class TopcoverMaterial(models.Model):
    _name = "topcover.material"

    name = fields.Char(required=True)
