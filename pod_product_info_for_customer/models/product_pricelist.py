from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("partner", "Partner Prices on the product form")],
        ondelete={"partner": "set default"},
    )
