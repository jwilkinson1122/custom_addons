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
        default="order_info",
        required=True,
    )

    allow_back = fields.Boolean(compute="_compute_allow_back")

    section_data = fields.Json(
        string="Section Data",
        default=lambda self: {},  # Use lambda to return an empty dict
        required=True,
    )

    # Laterality Field
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

    # Dynamic State Options
    @api.model
    def _selection_state(self):
        return [
            ("order_info", "Order Info"),
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

    # @api.model
    # def create(self, vals):
    #     vals["section_data"] = self._sanitize_section_data(vals.get("section_data", {}))
    #     return super().create(vals)

    def create(self, vals):
        _logger.debug(f"Before sanitizing section_data: {vals.get('section_data')}")
        vals["section_data"] = self._sanitize_section_data(vals.get("section_data", {}))
        _logger.debug(f"After sanitizing section_data: {vals['section_data']}")
        return super().create(vals)

    # def write(self, vals):
    #     if "section_data" in vals:
    #         vals["section_data"] = self._sanitize_section_data(vals["section_data"])
    #     return super().write(vals)

    def write(self, vals):
        if "section_data" in vals:
            _logger.debug(
                f"Before sanitizing section_data in write: {vals['section_data']}"
            )
            vals["section_data"] = self._sanitize_section_data(vals["section_data"])
            _logger.debug(
                f"After sanitizing section_data in write: {vals['section_data']}"
            )
        return super().write(vals)

    # Generic Data Handling
    def _initialize_section_data(self):
        if not isinstance(self.section_data, dict):
            _logger.warning(
                "Invalid section_data detected. Resetting to empty dictionary."
            )
            self.section_data = {}

    def _save_current_state(self):
        self.ensure_one()
        self._initialize_section_data()
        current_data = self._get_current_state_data()
        self.section_data[self.state] = current_data
        _logger.info(f"Saved data for state '{self.state}': {current_data}")

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
        self._initialize_section_data()
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
        """Ensure section_data is properly initialized."""
        defaults = super().default_get(fields_list)
        if "section_data" in fields_list:
            _logger.debug(f"Default section_data value: {defaults.get('section_data')}")
            defaults["section_data"] = {}
        return defaults

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
        _logger.debug(f"Sanitizing section_data: {data} (type: {type(data)})")
        if not data or isinstance(data, bool):
            return {}
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                _logger.warning(f"Invalid JSON for section_data: {data}")
                return {}
        return {}

    # Wizard Submission
    def submit_wizard(self):
        """Finalize the wizard and execute submission logic."""
        if not self.section_data:
            raise ValidationError(_("No section data available for submission."))

        _logger.info(f"Submitting wizard data: {self.section_data}")
        # Placeholder for submission logic.
        self._finalize_submission()

    def _finalize_submission(self):
        """Override to implement submission logic in subclasses."""
        raise NotImplementedError(_("Submission logic must be implemented in subclass"))
