import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class MultiStepWizard(models.AbstractModel):
    _name = "multi.step.wizard.mixin"
    _description = "Multi Steps Wizard Mixin"

    state = fields.Selection(
        selection="_selection_state", default="start", required=True
    )
    allow_back = fields.Boolean(compute="_compute_allow_back")

    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            # Allow back if a state_previous method exists for the current state
            record.allow_back = hasattr(record, f"state_previous_{record.state}")

    def state_previous_configure(self):
        self.state = "start"

    def state_previous_custom(self):
        self.state = "configure"

    def state_previous_summary(self):
        self.state = "custom"

    @api.model
    def _selection_state(self):
        return [
            ("start", "Start"),
            ("configure", "Configure"),
            ("custom", "Customize"),
            ("summary", "Summary"),
            ("final", "Final"),
        ]

    def open_next(self):
        state_method = getattr(self, f"state_exit_{self.state}", None)
        if not state_method:
            raise NotImplementedError(f"No method defined for state {self.state}")
        state_method()
        return self._reopen_self()

    def open_previous(self):
        state_method = getattr(self, f"state_previous_{self.state}", None)
        if not state_method:
            raise NotImplementedError(f"No method defined for state {self.state}")
        state_method()
        return self._reopen_self()

    def _reopen_self(self):
        _logger.info(f"Reopening wizard: id={self.id}, state={self.state}")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def state_exit_start(self):
        """Transition from Start state."""
        if not self.start_product_id:
            raise ValidationError(_("Please select a product in the Start section."))
        _logger.info(f"Exiting Start state with product: {self.start_product_id}")
        self.state = "configure"

    def state_exit_configure(self):
        """Transition from Configure state."""
        if not self.configure_product_id:
            raise ValidationError(
                _("Please select a product in the Configure section.")
            )
        _logger.info(
            f"Exiting Configure state with product: {self.configure_product_id.name}"
        )
        self.state = "custom"

    def state_exit_custom(self):
        """Transition from Custom state."""
        if not self.field3:
            raise ValidationError(_("Please provide customization details."))
        _logger.info(f"Exiting Custom state with customization: {self.field3}")
        self.state = "summary"

    def submit_wizard(self):
        """Submit the wizard and redirect back to the sales order form view."""
        if not self.sale_order_id:
            raise ValidationError(_("No associated sales order found."))

        if not self.start_product_id and not self.configure_product_id:
            raise ValidationError(_("No product selected for this wizard."))

        # Log details for debugging
        _logger.info(
            f"Submitting wizard: sale_order_id={self.sale_order_id.id}, "
            f"start_product_id={self.start_product_id.id if self.start_product_id else 'None'}, "
            f"configure_product_id={self.configure_product_id.id if self.configure_product_id else 'None'}, "
            f"field1={self.field1}, field2={self.field2}, field3={self.field3}"
        )

        # Combine descriptions for both products if available
        description = ""
        if self.start_product_id:
            description += f"Start Product: {self.start_product_id.display_name}\n"
        if self.start_selected_attribute_value_ids:
            start_attributes = ", ".join(
                self.start_selected_attribute_value_ids.mapped("name")
            )
            description += f"Start Attributes: {start_attributes}\n"
        if self.configure_product_id:
            description += (
                f"Configure Product: {self.configure_product_id.display_name}\n"
            )
        if self.configure_selected_attribute_value_ids:
            configure_attributes = ", ".join(
                self.configure_selected_attribute_value_ids.mapped("name")
            )
            description += f"Configure Attributes: {configure_attributes}\n"
        description += (
            f"Configuration 1: {self.field1 or 'N/A'}\n"
            f"Configuration 2: {self.field2 or 'N/A'}\n"
            f"Customization: {self.field3 or 'N/A'}"
        )

        # Use the product from the "Configure" step if it exists, otherwise the "Start" step
        product_id = (
            self.configure_product_id.id
            if self.configure_product_id
            else self.start_product_id.id
        )

        # Create the sale order line
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_id.id,
                "product_id": product_id,
                "product_uom_qty": 1,
                "price_unit": self.computed_price,
                "name": description,
            }
        )

        # Redirect back to the sale order
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
            "target": "current",
        }
