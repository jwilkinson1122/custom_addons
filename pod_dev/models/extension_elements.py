from odoo import models, api, fields


class ExtensionType(models.Model):
    _name = "extension.type"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920,
                          max_height=1920, widget=True)


class ExtensionMaterial(models.Model):
    _name = "extension.material"

    name = fields.Char(required=True)


class ExtensionLength(models.Model):
    _name = "extension.length"

    name = fields.Char(required=True)


class ExtensionThickness(models.Model):
    _name = "extension.thickness"

    name = fields.Char(required=True)
