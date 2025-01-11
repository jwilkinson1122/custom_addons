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
    product_id = fields.Many2one("product.product", string="Product", required=True)
    attribute_ids = fields.Many2many("product.attribute.value", string="Attributes")
    price = fields.Float(string="Price", digits="Product Price", required=True)

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
