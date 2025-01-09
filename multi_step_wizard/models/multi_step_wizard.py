import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MultiStepWizardMixin(models.AbstractModel):
    _name = "multi.step.wizard.mixin"
    _description = "Multi-Step Wizard Mixin"

    # Core Fields
    state = fields.Selection(
        selection="_selection_state",
        default="shell_foundation",
        required=True,
    )

    allow_back = fields.Boolean(compute="_compute_allow_back")

    section_data = fields.Json(
        string="Section Data",
        default="{}",  # Use string default
        required=False,  # Change to False
        copy=False,
    )

    laterality = fields.Selection(
        [
            ("left", "Left Only"),
            ("right", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Laterality",
        default="bilateral",
        required=True,
        help="Determines configuration options for left, right, or both sides.",
    )

    def state_next_shell_foundation(self):
        """Transition from shell_foundation to arch_height."""
        self.state = "arch_height"

    def state_next_arch_height(self):
        """Transition from arch_height to top_cover."""
        self.state = "top_cover"

    def state_next_top_cover(self):
        """Transition from top_cover to bottom_cover."""
        self.state = "bottom_cover"

    def state_next_bottom_cover(self):
        """Transition from bottom_cover to cushion."""
        self.state = "cushion"

    def state_next_cushion(self):
        """Transition from cushion to extension."""
        self.state = "extension"

    def state_next_extension(self):
        """Transition from extension to options."""
        self.state = "options"

    def state_next_options(self):
        """Transition from options to summary."""
        self.state = "summary"

    def state_next_summary(self):
        """Transition from summary to final."""
        self.state = "final"

    def state_previous_arch_height(self):
        """Go back to shell_foundation."""
        self.state = "shell_foundation"

    def state_previous_top_cover(self):
        """Go back to arch_height."""
        self.state = "arch_height"

    def state_previous_bottom_cover(self):
        """Go back to top_cover."""
        self.state = "top_cover"

    def state_previous_cushion(self):
        """Go back to bottom_cover."""
        self.state = "bottom_cover"

    def state_previous_extension(self):
        """Go back to cushion."""
        self.state = "cushion"

    def state_previous_options(self):
        """Go back to extension."""
        self.state = "extension"

    def state_previous_summary(self):
        """Go back to options."""
        self.state = "options"

    def state_previous_final(self):
        """Go back to summary."""
        self.state = "summary"

    # Dynamic State Options
    @api.model
    def _selection_state(self):
        return [
            ("shell_foundation", "Shell / Foundation"),
            ("arch_height", "Arch Height"),
            ("top_cover", "Top Cover"),
            ("bottom_cover", "X-Guard"),
            ("cushion", "Cushion"),
            ("extension", "Extension"),
            ("options", "Options"),
            ("summary", "Summary"),
            ("final", "Final"),
        ]

    # Navigation and State Management
    @api.depends("state")
    def _compute_allow_back(self):
        """Determine if navigation to the previous state is allowed."""
        for record in self:
            record.allow_back = hasattr(record, f"state_previous_{record.state}")
            _logger.debug(
                f"Computed 'allow_back' for state '{record.state}': {record.allow_back}"
            )

    def open_next(self):
        """Transition to the next state."""
        _logger.info(f"Transitioning to the next state from '{self.state}'.")
        self._save_current_state()
        self._handle_state_transition("next")
        return self._reopen_wizard()

    def open_previous(self):
        """Transition to the previous state."""
        _logger.info(f"Transitioning to the previous state from '{self.state}'.")
        self._restore_previous_state()
        self._handle_state_transition("previous")
        return self._reopen_wizard()

    def _handle_state_transition(self, direction):
        """Handle state transitions dynamically."""
        method_name = f"state_{direction}_{self.state}"
        if not hasattr(self, method_name):
            raise NotImplementedError(
                f"No method defined for state transition: {method_name}"
            )
        getattr(self, method_name)()
        _logger.info(f"State transitioned to: {self.state}")

    def _init_section_data(self):
        """Initialize section_data if it's not a valid dictionary."""
        try:
            _logger.debug(f"Current section_data before init: {self.section_data}")
            if not self.section_data or not isinstance(self.section_data, dict):
                _logger.debug("Initializing section_data to empty dict")
                self.write({"section_data": {}})
            _logger.debug(f"Section_data after init: {self.section_data}")
        except Exception as e:
            _logger.error(f"Error initializing section_data: {str(e)}")
            self.write({"section_data": {}})

    @api.model
    def create(self, vals):
        if "section_data" not in vals:
            vals["section_data"] = "{}"
        return super().create(vals)

    def write(self, vals):
        if "section_data" in vals and not vals["section_data"]:
            vals["section_data"] = "{}"  # Use string representation
        return super().write(vals)

    @api.onchange("section_data")
    def _onchange_section_data(self):
        """Ensure section_data is always initialized."""
        if not self.section_data:
            self.section_data = "{}"  # Use string representation

    def _update_section_data(self):
        """Safely update section data for the current state."""
        try:
            self._init_section_data()
            if self.state:
                current_data = {
                    "section_price": self.section_price,
                    "product_id": (
                        self.section_product_id.id if self.section_product_id else False
                    ),
                    "attribute_ids": (
                        self.section_attribute_ids.ids
                        if self.section_attribute_ids
                        else []
                    ),
                }
                self.write(
                    {"section_data": {**self.section_data, self.state: current_data}}
                )
        except Exception as e:
            _logger.error(f"Error updating section data: {str(e)}")

    def _save_current_state(self):
        self.ensure_one()
        if not isinstance(self.section_data, dict):
            _logger.error(
                f"Invalid section_data detected before saving: {self.section_data}"
            )
            self.section_data = {}
        current_data = self._get_current_state_data()
        _logger.debug(f"Current state data for '{self.state}': {current_data}")
        if current_data:
            try:
                self.section_data[self.state] = current_data
                _logger.info(
                    f"Successfully saved data for state '{self.state}': {current_data}"
                )
            except Exception as e:
                _logger.error(f"Error saving current state data: {str(e)}")

    def _get_current_state_data(self):
        self.ensure_one()
        return {
            "laterality": self.laterality,
            "product_id": (
                self.section_product_id.id
                if hasattr(self, "section_product_id") and self.section_product_id
                else False
            ),
            "attribute_ids": (
                self.section_attribute_ids.ids
                if hasattr(self, "section_attribute_ids")
                else []
            ),
            "section_price": (
                self.section_price if hasattr(self, "section_price") else 0.0
            ),
        }

    def _restore_previous_state(self):
        self.ensure_one()
        self._init_section_data()
        previous_state = self._get_previous_state()
        if previous_state and previous_state in self.section_data:
            previous_data = self.section_data[previous_state]
            self._set_state_data(previous_data)

    def _apply_state_data(self, data):
        """Apply data for the current state. Override in subclasses."""
        if not data:
            return
        self.laterality = data.get("laterality", "bilateral")

    def _get_section_price(self):
        """Calculate the price for the current section."""
        return 0.0

    def _get_previous_state(self):
        states = self._selection_state()
        current_index = next(
            (i for i, (state, _) in enumerate(states) if state == self.state), -1
        )
        return states[current_index - 1][0] if current_index > 0 else None

    def _get_state_list(self):
        """Get list of states without labels."""
        return [state[0] for state in self._selection_state()]

    def _get_state_label(self, state_code):
        """Get the label for a state code."""
        for code, label in self._selection_state():
            if code == state_code:
                return label
        return ""

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "section_data" in fields_list:
            res["section_data"] = "{}"  # Use string representation
        return res

    def _ensure_section_data(self):
        """Ensure section_data is a valid dictionary."""
        if not isinstance(self.section_data, dict):
            self.section_data = {}

    @api.onchange("section_product_id", "section_attribute_ids", "section_price")
    def _onchange_section_selections(self):
        self._init_section_data()
        self._update_section_data()

    def _set_state_data(self, data):
        self.ensure_one()
        if not data or not isinstance(data, dict):
            _logger.warning(f"Invalid data format received: {data}")
            return

        for field, value in data.items():
            if hasattr(self, field):
                try:
                    setattr(self, field, value)
                except Exception as e:
                    _logger.error(f"Error setting field {field}: {str(e)}")

    def _reopen_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _sanitize_section_data(self, data):
        """Ensure section_data is a valid dictionary."""
        _logger.debug(f"Sanitizing section_data: {data} (type: {type(data)})")
        if not isinstance(data, dict):
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                    if not isinstance(data, dict):
                        raise ValueError("Parsed JSON is not a dictionary.")
                else:
                    raise ValueError("Data is not a valid dictionary or JSON string.")
            except (ValueError, json.JSONDecodeError) as e:
                _logger.error(
                    f"Invalid section_data detected: {data}. Resetting to {{}}."
                )
                data = {}
        return data

    def submit_wizard(self):
        """Finalize the wizard and execute submission logic."""
        if not self.section_data:
            raise ValidationError(_("No section data available for submission."))

        _logger.info(f"Submitting wizard data: {self.section_data}")
        self._finalize_submission()

    def _finalize_submission(self):
        """Override to implement submission logic in subclasses."""
        raise NotImplementedError(_("Submission logic must be implemented in subclass"))
