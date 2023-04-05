from odoo import fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    measure_type = fields.Selection(
        string="Type of Measure",
        related="category_id.measure_type",
        store=True,
        readonly=True,
    )
