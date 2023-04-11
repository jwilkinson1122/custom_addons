from odoo import fields, models


class UomCategory(models.Model):
    _inherit = "uom.category"

    measure_type = fields.Selection(
        string="Type of Measure",
        selection=[
            ("unit", "Units"),
            ("pairs", "Pairs"),
            ("weight", "Weight"),
            ("working_time", "Working Time"),
            ("length", "Length"),
            ("width", "Width"),
            ("surface", "Surface"),
            ("volume", "Volume"),
        ],
        required=True,
    )

    _sql_constraints = [
        (
            "uom_category_unique_type",
            "UNIQUE(measure_type)",
            "You can have only one category per measurement type.",
        ),
    ]
