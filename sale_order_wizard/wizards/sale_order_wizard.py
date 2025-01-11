import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _inherit = "sale.order.wizard.mixin"
    _description = "Sale Order Wizard"

    sale_order_id = fields.Many2one(
        "sale.order", default=lambda self: self.env.context.get("active_id")
    )
    product_id = fields.Many2one(
        "product.product", domain="[('id', 'in', available_product_ids)]"
    )
    section_product_ids = fields.One2many(
        "sale.order.section.product", "wizard_id", string="Section Products"
    )
    available_product_ids = fields.Many2many(
        "product.product", compute="_compute_available_products"
    )
    product_attribute_ids = fields.Many2many("product.attribute.value")
    # section_price = fields.Float(compute="_compute_section_price")
    # total_price = fields.Float(compute="_compute_total_price")
    summary = fields.Text(compute="_compute_summary")

    @api.depends("state")
    def _compute_available_products(self):
        """Get available products for the current section."""
        for record in self:
            section = self.env["sale.order.section"].search(
                [("section_name", "=", record.state)], limit=1
            )
            record.available_product_ids = (
                self.env["product.product"].search(
                    [("categ_id", "child_of", section.product_category_id.id)]
                )
                if section
                else self.env["product.product"]
            )

    @api.depends("product_id", "product_attribute_ids")
    def _compute_section_price(self):
        for record in self:
            base_price = record.product_id.list_price or 0.0
            attribute_extra_price = sum(
                ptav.price_extra
                for ptav in self.env["product.template.attribute.value"].search(
                    [
                        ("product_tmpl_id", "=", record.product_id.product_tmpl_id.id),
                        (
                            "product_attribute_value_id",
                            "in",
                            record.product_attribute_ids.ids,
                        ),
                    ]
                )
            )
            record.section_price = base_price + attribute_extra_price

    @api.depends("section_product_ids.price")
    def _compute_total_price(self):
        for record in self:
            record.total_price = sum(
                selection.price for selection in record.section_product_ids
            )

    @api.depends("state", "section_product_ids")
    def _compute_summary(self):
        for record in self:
            record.summary = "\n".join(
                f"{selection.section_name}: {selection.product_id.name} - {selection.price}"
                for selection in record.section_product_ids
            )
