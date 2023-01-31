from odoo import models, api, fields


class ShellLength(models.Model):
    _name = "shell.length"

    name = fields.Char(required=True)


class ShellType(models.Model):
    _name = "shell.type"

    name = fields.Char(required=True)
    image = fields.Binary("Image", max_width=1920,
                          max_height=1920, widget=True)


class ShellTypes(models.Model):
    _name = "shell.collection"

    name = fields.Char(required=True)
    type = fields.Many2one('shell.type', string='Type')
