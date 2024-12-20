from odoo import models, api, fields


class LensType(models.Model):
    _name = "lens.type"

    name = fields.Char(required=True)


class LensStyle(models.Model):
    _name = "lens.style"

    name = fields.Char(required=True)


class LensMaterial(models.Model):
    _name = "lens.material"

    name = fields.Char(required=True)
