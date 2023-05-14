# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PatientBreed(models.Model):
    _name = "patient.breed"
    _description = "Patient Breeds"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    species_id = fields.Many2one("patient.species", string="Species", required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
