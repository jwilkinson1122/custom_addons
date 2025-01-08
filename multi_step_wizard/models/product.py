from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    laterality = fields.Selection(
        [
            ("left", "Left Only"),
            ("right", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Laterality",
        help="Specifies if the product is for left side, right side, or bilateral use",
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    laterality = fields.Selection(
        [
            ("left", "Left Only"),
            ("right", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Laterality",
        help="Specifies if the product is for left side, right side, or bilateral use",
    )
