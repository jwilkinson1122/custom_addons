from odoo import models, fields, api

class Insurance(models.Model):
    _name = "animal.insurance"
    _description = "Animals insurances table"

    name = fields.Char(string="Insurance", required=True)
    characteristics = fields.Text(string="Characteristics")
    cost = fields.Integer(string="Cost")
