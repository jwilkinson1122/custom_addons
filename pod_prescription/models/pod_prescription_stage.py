from odoo import fields, models


class PrescriptionStage(models.Model):
    _name = "pod.prescription.stage"
    _description = "Prescription Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "Requested"),
            ("open", "Borrowed"),
            ("done", "Returned"),
            ("cancel", "Canceled"),
        ],
        default="new",
    )
