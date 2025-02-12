from odoo import api, fields, models


class PriceListItem(models.Model):
    _inherit = "product.pricelist.item"

    price_tire_ids = fields.One2many(
        "tire.list",
        "price_list_id",
        string="Tires",
    )

    compute_price = fields.Selection(
        selection=[
            ('fixed', "Fixed Price"),
            ('percentage', "Discount"),
            ('formula', "Formula"),
            ('tiered', "Tiered")
        ],
        index=True, default='fixed', required=True
    )

    price_list_product_id = fields.Many2one("product.product", string="Product Variant")