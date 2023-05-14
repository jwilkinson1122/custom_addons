# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PatientColor(models.Model):
    _name = "patient.color"
    _description = "Patient Colors"

    name = fields.Char(string="Name", translate=True)
    breed_id = fields.Many2one("patient.breed", string="Breed", required=True)
    species_id = fields.Many2one(
        "patient.species", string="Species", related="breed_id.species_id", readonly=True
    )
