from odoo import fields, models


class medical_prescription_order_stage(models.Model):
    _name = "medical.prescription.order.stage"
    _description = "Prescription Order Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            # ("in_process", "In Process"),
            ("done", "Done"),
            ("cancel", "Cancel"),
            ("hold", "Hold"),
        ],
        default="draft",
    )
