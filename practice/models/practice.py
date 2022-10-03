# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Practice(models.Model):
    _name = "practice"
    _description = "Practice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name")
    ref = fields.Char(string="Reference")
    type_id = fields.Many2one(
        "practice.type", string="Type", required=True)
    specialty_id = fields.Many2one(
        "practice.specialty", string="Specialty", required=True)
    size = fields.Char(string="Size")
    weight = fields.Float(string="Weight (in kg)")
    birth_date = fields.Date(string="Birth Date")
    gender = fields.Selection(
        string="Gender",
        selection=[
            ("female", "Female"),
            ("male", "Male"),
            ("hermaphrodite", "Hermaphrodite"),
            ("neutered", "Neutered"),
        ],
        default="female",
        required=True,
    )
    active = fields.Boolean(default=True)
    image = fields.Binary(
        "Image", attachment=True, help="This field holds the photo of the practice."
    )

    @api.onchange("type_id")
    def onchange_type(self):
        self.specialty_id = False

    # @api.onchange("specialty_id")
    # def onchange_specialty(self):
    #     self.color_id = False
