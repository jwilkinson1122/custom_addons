from odoo import models, api, fields


class ShellMaterial(models.Model):
    _name = "shell.material"

    name = fields.Char(required=True)


class ShellShape(models.Model):
    _name = "shell.shape"

    name = fields.Char(required=True)


class ShellType(models.Model):
    _name = "shell.type"

    name = fields.Char(required=True)


class ShellManufacturer(models.Model):
    _name = "shell.manufacturer"

    name = fields.Char(required=True)


class ShellBrands(models.Model):
    _name = "shell.brand"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920, max_height=1920, widget=True)


class ShellBrands(models.Model):
    _name = "shell.collection"

    name = fields.Char(required=True)
    brand = fields.Many2one('shell.brand', string='Brand')
