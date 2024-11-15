from odoo import models, fields, api

class Allergy(models.Model):
    _name = "animal.allergy"
    _description = "Animal allergies table"

    name = fields.Char(string="Allergies", required=True)
    description = fields.Text(string="Description")
