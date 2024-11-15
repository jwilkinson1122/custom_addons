from odoo import models, fields, api

class Vaccine(models.Model):
    _name = "animal.vaccine"
    _description = "Animal vaccines table"

    name = fields.Char(string="Vaccine", required=True)
    description = fields.Text(string="Description")
