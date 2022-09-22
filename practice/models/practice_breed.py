

from odoo import fields, models


class PracticeBreed(models.Model):
    _name = "practice.breed"
    _description = "Practice Breeds"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    species_id = fields.Many2one(
        "practice.species", string="Species", required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
