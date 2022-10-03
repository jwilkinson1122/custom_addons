# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PracticeSpecialty(models.Model):
    _name = "practice.specialty"
    _description = "Practice Specialties"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    type_id = fields.Many2one(
        "practice.type", string="Type", required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
