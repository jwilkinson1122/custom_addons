import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class SaleOrderSection(models.Model):
    _name = "sale.order.section"
    _description = "Sale Order Section"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    section_name = fields.Char(string="Section Identifier", required=True)
    description = fields.Text(string="Section Description")
    product_category_id = fields.Many2one(
        "product.category", string="Product Category", required=True
    )
    is_required = fields.Boolean(string="Is Required", default=False)

    _sql_constraints = [
        ("unique_section_name", "unique(section_name)", "Section name must be unique."),
    ]
