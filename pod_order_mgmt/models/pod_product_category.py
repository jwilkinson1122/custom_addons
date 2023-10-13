
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    total_route_ids = fields.Many2many(
        domain=lambda self: [
            "|",
            ("company_id", "=", False),
            ("company_id", "in", self.env.companies.ids),
        ]
    )

    route_ids = fields.Many2many(
        "stock.location.route",
        "stock_location_route_categ",
        "categ_id",
        "route_id",
        "Routes",
        domain=lambda self: [
            "|",
            ("company_id", "=", False),
            ("company_id", "in", self.env.companies.ids),
        ],
    )
