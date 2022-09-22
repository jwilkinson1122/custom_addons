

from odoo import fields, models


class PracticeSpecies(models.Model):
    _name = "practice.species"
    _description = "Practice Species"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
    breed_ids = fields.One2many(
        "practice.breed", "species_id", string="Breeds")
