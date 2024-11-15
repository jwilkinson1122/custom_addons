from odoo import models, fields, api

class Tag(models.Model):
    _name = "animal.tag"
    _description = "Animal tags table"

    name = fields.Char(string="Tag", required=True)
    description = fields.Text(string="Description")
    color = fields.Integer(string="Color")
