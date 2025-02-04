import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderSectionProduct(models.TransientModel):
    _name = "sale.order.section.product"
    _description = "Sale Order Section Product"

    wizard_id = fields.Many2one(
        "sale.order.wizard", string="Wizard", required=True, ondelete="cascade"
    )
    section_name = fields.Char(string="Section Name", required=True)
    # product_id = fields.Many2one("product.product", string="Product", required=True)
    # attribute_ids = fields.Many2many("product.attribute.value", string="Attributes")
    product_id = fields.Many2one("product.product", string="Product", required=False)
    product_ids = fields.Many2many(
        "product.product", string="Products", domain="[('sale_ok', '=', True)]"
    )
    product_attribute_ids = fields.One2many(
        "sale.order.section.product.attribute",
        "section_product_id",
        string="Attributes",
    )
    price = fields.Float(compute="_compute_total_price", string="Total Price")

    @api.depends("product_ids", "product_attribute_ids")
    def _compute_total_price(self):
        """Compute the total price for all selected products and attributes."""
        for record in self:
            product_price = sum(product.list_price for product in record.product_ids)
            attribute_price = sum(
                attr.price_extra for attr in record.product_attribute_ids
            )
            record.price = product_price + attribute_price

    def clear_section(self):
        self.ensure_one()

        if not self.state:
            raise ValidationError(
                _("The wizard is not in a valid state to clear the section.")
            )

        _logger.info(f"Resetting section '{self.state}' for wizard {self.id}.")

        # Fetch existing selections for the current section
        existing_selections = self.env["sale.order.section.product"].search(
            [("wizard_id", "=", self.id), ("section_name", "=", self.state)]
        )

        if not existing_selections:
            _logger.warning(
                f"No existing selections found to clear for section '{self.state}' in wizard {self.id}."
            )

        # Clear the current selections
        self.product_id = False
        self.attribute_ids = [(5, 0, 0)]
        self.price = 0.0

        # Remove saved selections and handle errors
        try:
            existing_selections.unlink()
            _logger.info(
                f"Cleared saved selections for section '{self.state}' in wizard {self.id}."
            )
        except Exception as e:
            _logger.error(
                f"Error while clearing selections for section '{self.state}' in wizard {self.id}: {str(e)}"
            )
            raise ValidationError(
                _("An error occurred while clearing the section. Please try again.")
            )

        # Reopen the wizard to reflect changes
        # return self._reopen_wizard()

    def clear_all(self):
        self.ensure_one()

        _logger.info(f"Clearing all sections for wizard {self.id}.")

        # Remove all saved selections
        self.env["sale.order.section.product"].search(
            [("wizard_id", "=", self.id)]
        ).unlink()

        # Reset the wizard to the initial state
        self.product_id = False
        self.attribute_ids = [(5, 0, 0)]
        self.price = 0.0
        # self.state = "shell_foundation"
        # return self._reopen_wizard()


class SaleOrderSectionProductAttribute(models.TransientModel):
    _name = "sale.order.section.product.attribute"
    _description = "Sale Order Section Product Attribute"

    section_product_id = fields.Many2one(
        "sale.order.section.product",
        string="Section Product",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one("product.product", string="Product", required=True)
    attribute_id = fields.Many2one(
        "product.attribute.value", string="Attribute", required=True
    )
    price_extra = fields.Float(string="Extra Price", required=True)

    @api.onchange("attribute_id")
    def _onchange_attribute_id(self):
        """Update price_extra based on the selected attribute."""
        if self.attribute_id:
            ptav = self.env["product.template.attribute.value"].search(
                [
                    ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                    ("product_attribute_value_id", "=", self.attribute_id.id),
                ],
                limit=1,
            )
            self.price_extra = ptav.price_extra if ptav else 0.0


# class SaleOrderSectionProduct(models.TransientModel):
#     _name = "sale.order.section.product"
#     _description = "Sale Order Section Product"

#     wizard_id = fields.Many2one(
#         "sale.order.wizard", string="Wizard", required=True, ondelete="cascade"
#     )
#     section_name = fields.Selection(
#         selection=lambda self: self._get_selection_state(),
#         string="Section Name",
#         required=True,
#     )
#     product_id = fields.Many2one(
#         "product.product", string="Product", required=True, ondelete="restrict"
#     )
#     attribute_ids = fields.Many2many("product.attribute.value", string="Attributes")
#     price = fields.Float(string="Price", digits="Product Price", required=True)

#     def _get_selection_state(self):
#         """Get selection values from SaleOrderWizardMixin."""
#         return self.env["sale.order.wizard.mixin"]._selection_state()
