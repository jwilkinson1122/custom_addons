

from odoo import fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    reference_format = fields.Char(default="%.2f")
