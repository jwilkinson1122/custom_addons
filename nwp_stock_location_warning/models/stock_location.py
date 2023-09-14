

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    warning = fields.Text(string="Warning")
