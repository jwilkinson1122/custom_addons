from odoo import fields, models


class BookoutStage(models.Model):
    _name = "clinic.bookout.stage"
    _description = "Bookout Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "Requested"),
            ("open", "Received"),
            ("done", "Complete"),
            ("cancel", "Cancelled"),
        ],
        default="new",
    )
