from odoo import fields, models


class EstateTag(models.Model):
    _name = "estate.tag"
    _description = "Estate Tag"

    name = fields.Char(string="Label", required=True)
    color = fields.Integer(string="Color")
