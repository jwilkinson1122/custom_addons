from odoo import models, api, fields


class ShellFoundationType(models.Model):
    _name = "shell.foundation.type"

    name = fields.Char(required=True)

class ShellFoundationBrand(models.Model):
    _name = "shell.foundation.brand"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920, max_height=1920, widget=True)


class ShellFoundationCollection(models.Model):
    _name = "shell.foundation.collection"

    name = fields.Char(required=True)
    brand = fields.Many2one('shell.foundation.brand', string='Brand')
