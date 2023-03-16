from odoo import models, api, fields


class CushionType(models.Model):
    _name = "cushion.type"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920,
                          max_height=1920, widget=True)


class CushionMaterial(models.Model):
    _name = "cushion.material"

    name = fields.Char(required=True)


class CushionLength(models.Model):
    _name = "cushion.length"

    name = fields.Char(required=True)


class CushionThickness(models.Model):
    _name = "cushion.thickness"

    name = fields.Char(required=True)
