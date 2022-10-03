# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PracticeType(models.Model):
    _name = "practice.type"
    _description = "Practice Type"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
    specialty_ids = fields.One2many(
        "practice.specialty", "type_id", string="Specialties")
