from odoo import fields, models


class PrescriptionStage(models.Model):
    _name = "podiatry.prescription.stage"
    _description = "Prescription Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("confirm", "Confirm"),
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        default="confirm",
    )
    