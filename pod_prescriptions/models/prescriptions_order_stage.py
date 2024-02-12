from odoo import fields, models


class PrescriptionStage(models.Model):
    _name = "prescriptions.order.stage"
    _description = "Prescription Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Confirmed"),
            ("cancel", "Canceled"),
            ("hold", "On Hold"),
        ],
        default="draft",
    )
