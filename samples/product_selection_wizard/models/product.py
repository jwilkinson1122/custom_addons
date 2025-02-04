import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # laterality = fields.Selection(
    #     [
    #         ("left", "Left Only"),
    #         ("right", "Right Only"),
    #         ("bilateral", "Bilateral"),
    #     ],
    #     string="Laterality",
    #     help="Specifies if the product is for left side, right side, or bilateral use",
    # )

    laterality = fields.Selection(
        [
            ("left", "Left Only"),
            ("right", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Laterality",
        default="bilateral",
        help="Left Only, Right Only, or Bilateral",
    )

    section_id = fields.Many2one(
        "product.section.configuration",
        string="Section",
        help="Specify the section this product belongs to.",
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    # laterality = fields.Selection(
    #     [
    #         ("left", "Left Only"),
    #         ("right", "Right Only"),
    #         ("bilateral", "Bilateral"),
    #     ],
    #     string="Laterality",
    #     default="bilateral",
    #     help="Left Only, Right Only, or Bilateral",
    # )

    laterality_price = fields.Float(
        string="Laterality Price",
        compute="_compute_laterality_price",
        store=True,
    )

    @api.depends("laterality", "list_price")
    def _compute_laterality_price(self):
        for product in self:
            if product.laterality == "left":
                product.laterality_price = product.list_price
            elif product.laterality == "right":
                product.laterality_price = product.list_price
            elif product.laterality == "bilateral":
                product.laterality_price = product.list_price * 2

    # @api.depends("laterality", "product_template_attribute_value_ids")
    # def _compute_laterality_price(self):
    #     for product in self:
    #         base_price = product.list_price
    #         color_price = sum(
    #             ptav.price_extra
    #             for ptav in product.product_template_attribute_value_ids
    #             if ptav.attribute_id.name == "Color"
    #         )
    #         if product.laterality == "left":
    #             product.laterality_price = base_price + color_price
    #         elif product.laterality == "right":
    #             product.laterality_price = base_price + color_price
    #         elif product.laterality == "bilateral":
    #             product.laterality_price = (base_price + color_price) * 2

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
