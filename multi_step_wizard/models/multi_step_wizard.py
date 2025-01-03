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

    section_data = fields.Json(
        string="Section Data",
        help="Stores data for each section of the wizard, such as selected products and attributes.",
        default=dict,  # Initialize as an empty dictionary
    )

    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            record.allow_back = hasattr(record, f"state_previous_{record.state}")
            _logger.debug(
                f"Computed 'allow_back' for state '{record.state}': {record.allow_back}"
            )

    def state_previous_configure(self):
        _logger.info("Transitioning to the 'start' state.")
        self.state = "start"

    def state_previous_custom(self):
        _logger.info("Transitioning to the 'configure' state.")
        self.state = "configure"

    def state_previous_summary(self):
        _logger.info("Transitioning to the 'custom' state.")
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

    def _initialize_section_data(self):
        """Ensure section_data is always a valid dictionary."""
        if not isinstance(self.section_data, dict):
            _logger.warning(
                f"Invalid section_data detected in record ID {self.id}. Resetting to an empty dictionary."
            )
            # Log the type and value of the invalid data
            _logger.debug(
                f"Invalid section_data type: {type(self.section_data)}, value: {self.section_data}"
            )
            self.section_data = {}
            _logger.info(f"section_data has been reset to: {self.section_data}")

    def _save_current_state(self):
        """Save the selections for the current state."""
        self._initialize_section_data()  # Ensure section_data is valid
        _logger.info(
            f"Saving current state: {self.state}. section_data before save: {self.section_data}"
        )

        try:
            if self.state == "start":
                self.section_data["start"] = {
                    "product_id": (
                        self.start_product_id.id if self.start_product_id else False
                    ),
                    "attributes": self.start_selected_attribute_value_ids.ids,
                }
            elif self.state == "configure":
                self.section_data["configure"] = {
                    "product_id": (
                        self.configure_product_id.id
                        if self.configure_product_id
                        else False
                    ),
                    "attributes": self.configure_selected_attribute_value_ids.ids,
                }
            _logger.info(f"section_data after save: {self.section_data}")
        except Exception as e:
            _logger.error(f"Failed to save current state: {e}")
            raise ValidationError(_("An error occurred while saving the wizard state."))

    @api.model
    def create(self, vals):
        """Ensure section_data is valid during creation."""
        _logger.info(f"Creating wizard with values: {vals}")
        if "section_data" not in vals or not isinstance(vals.get("section_data"), dict):
            _logger.warning(
                f"Invalid section_data during creation: {vals.get('section_data')}"
            )
            vals["section_data"] = {}
            _logger.info(
                "Initialized section_data as an empty dictionary during creation."
            )
        return super().create(vals)

    def write(self, vals):
        """Ensure section_data is valid during updates."""
        if "section_data" in vals:
            if not isinstance(vals.get("section_data"), dict):
                _logger.error(
                    f"Invalid section_data detected in write operation for record ID {self.id}. "
                    f"Type: {type(vals['section_data'])}, Value: {vals['section_data']}"
                )
                vals["section_data"] = {}
                _logger.info("Resetting section_data to an empty dictionary.")
        return super().write(vals)

    def open_next(self):
        """Transition to the next step."""
        _logger.info(
            f"Attempting to transition from state '{self.state}' to the next state."
        )
        self._initialize_section_data()
        try:
            self._save_current_state()
        except ValidationError as e:
            _logger.warning(f"Failed to transition to the next state: {e}")
            raise e

        state_method = getattr(self, f"state_exit_{self.state}", None)
        if not state_method:
            _logger.error(f"No exit method defined for state '{self.state}'.")
            raise NotImplementedError(f"No method defined for state {self.state}")

        state_method()
        return self._reopen_self()

    def open_previous(self):
        """Transition to the previous step."""
        _logger.info(
            f"Attempting to transition from state '{self.state}' to the previous state."
        )

        state_method = getattr(self, f"state_previous_{self.state}", None)
        if not state_method:
            _logger.error(f"No previous method defined for state '{self.state}'.")
            raise NotImplementedError(f"No method defined for state {self.state}")

        state_method()
        self._restore_previous_state()
        return self._reopen_self()

    def _restore_previous_state(self):
        """Restore the selections for the previous state."""
        self._initialize_section_data()
        _logger.info(
            f"Restoring state: {self.state}, section_data: {self.section_data}"
        )

        if self.state == "start" and self.section_data.get("start"):
            self.start_product_id = self.env["product.product"].browse(
                self.section_data["start"].get("product_id")
            )
            self.start_selected_attribute_value_ids = [
                (6, 0, self.section_data["start"].get("attributes", []))
            ]
        elif self.state == "configure" and self.section_data.get("configure"):
            self.configure_product_id = self.env["product.product"].browse(
                self.section_data["configure"].get("product_id")
            )
            self.configure_selected_attribute_value_ids = [
                (6, 0, self.section_data["configure"].get("attributes", []))
            ]
        _logger.info(
            f"Restored fields: start_product_id={self.start_product_id}, configure_product_id={self.configure_product_id}"
        )

    def _reopen_self(self):
        _logger.info(
            f"Reopening wizard: id={self.id}, state={self.state}, section_data={self.section_data}"
        )
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
            _logger.error("No product selected in the Start section.")
            raise ValidationError(_("Please select a product in the Start section."))

        _logger.info(f"Exiting Start state with product: {self.start_product_id}")
        self.state = "configure"

    def state_exit_configure(self):
        """Transition from Configure state."""
        if not self.configure_product_id:
            _logger.error("No product selected in the Configure section.")
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
            _logger.error("Customization details are missing.")
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

        # Use start_product_id if available; otherwise, fallback to configure_product_id
        product_id = (
            self.start_product_id.id
            if self.start_product_id
            else self.configure_product_id.id
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
