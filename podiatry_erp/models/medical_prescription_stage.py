from odoo import fields, models


class PrescriptionStage(models.Model):
    _name = "medical.prescription.stage"
    _description = "Prescription Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "Requested"),
            ("open", "Open"),
            ("done", "Complete"),
            ("cancel", "Canceled"),
        ],
        default="new",
    )
