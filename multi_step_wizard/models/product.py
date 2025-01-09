import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


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

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        _logger.info(
            f"""
            Product Name Search Called:
            Name: {name}
            Args: {args}
            Operator: {operator}
            Limit: {limit}
        """
        )
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
