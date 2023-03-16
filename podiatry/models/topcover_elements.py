from odoo import models, api, fields


class TopcoverType(models.Model):
    _name = "topcover.type"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920,
                          max_height=1920, widget=True)


class TopcoverLength(models.Model):
    _name = "topcover.length"

    name = fields.Char(required=True)


class TopcoverMaterial(models.Model):
    _name = "topcover.material"

    name = fields.Char(required=True)


class TopcoverThickness(models.Model):
    _name = "topcover.thickness"
    name = fields.Char(required=True)


class TopcoverColor(models.Model):
    _name = "topcover.color"
    name = fields.Char(required=True)
    color = fields.Integer()
