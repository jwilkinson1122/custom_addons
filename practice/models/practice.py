

from odoo import api, fields, models


class Practice(models.Model):
    _name = "practice"
    _description = "Practice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name")
    ref = fields.Char(string="Reference")
    species_id = fields.Many2one(
        "practice.species", string="Species", required=True)
    breed_id = fields.Many2one("practice.breed", string="Breed", required=True)
    color_id = fields.Many2one("practice.color", string="Color")
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

    @api.onchange("species_id")
    def onchange_species(self):
        self.breed_id = False

    @api.onchange("breed_id")
    def onchange_breed(self):
        self.color_id = False
