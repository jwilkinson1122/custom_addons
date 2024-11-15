from odoo import models, fields, api 


class Specie(models.Model):
    _name = "animal.specie"
    _description = "Animals species table"

    name = fields.Char(string="Specie")
    characteristics = fields.Text(string="Characteristics")
