

from odoo import fields, models


class PracticeColor(models.Model):
    _name = "practice.color"
    _description = "Practice Colors"

    name = fields.Char(string="Name", translate=True)
    breed_id = fields.Many2one("practice.breed", string="Breed", required=True)
    species_id = fields.Many2one(
        "practice.species", string="Species", related="breed_id.species_id", readonly=True
    )
