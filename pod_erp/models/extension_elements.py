from odoo import models, api, fields


class ExtensionType(models.Model):
    _name = "extension.type"

    name = fields.Char(required=True)

class ExtensionLength(models.Model):
    _name = "extension.length"

    name = fields.Char(required=True)

class ExtensionMaterial(models.Model):
    _name = "extension.material"

    name = fields.Char(required=True)


class ExtensionDensity(models.Model):
    _name = "extension.density"

    name = fields.Char(required=True)

class ExtensionThickness(models.Model):
    _name = "extension.thickness"

    name = fields.Char(required=True)