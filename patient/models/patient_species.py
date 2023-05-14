# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PatientSpecies(models.Model):
    _name = "patient.species"
    _description = "Patient Species"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
    breed_ids = fields.One2many("patient.breed", "species_id", string="Breeds")
