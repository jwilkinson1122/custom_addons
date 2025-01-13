from odoo import models, api, fields


class CushionType(models.Model):
    _name = "cushion.type"

    name = fields.Char(required=True)

class CushionLength(models.Model):
    _name = "cushion.length"

    name = fields.Char(required=True)

class CushionMaterial(models.Model):
    _name = "cushion.material"

    name = fields.Char(required=True)


class CushionDensity(models.Model):
    _name = "cushion.density"

    name = fields.Char(required=True)

class CushionThickness(models.Model):
    _name = "cushion.thickness"

    name = fields.Char(required=True)