import logging
import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderWizardMixin(models.AbstractModel):
    _name = "sale.order.wizard.mixin"
    _description = "Sale Order Wizard Mixin"

    state = fields.Selection(selection="_get_dynamic_states", required=True)
    allow_back = fields.Boolean(compute="_compute_allow_back")

    section_data = fields.Json(
        string="Section Data", default={}, required=False, copy=False
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
    )

    @api.model
    def _get_dynamic_states(self):
        sections = self.env["sale.order.section"].search([], order="sequence")
        if not sections:
            _logger.warning("No sections found in SaleOrderSection.")
        return [
            (section.section_name, section.description or section.section_name)
            for section in sections
        ]

    @api.depends("state")
    def _compute_allow_back(self):
        first_state = (
            self._get_dynamic_states()[0][0] if self._get_dynamic_states() else None
        )
        for record in self:
            record.allow_back = record.state != first_state

    def _ensure_section_data(self):
        """Ensure section_data is a valid JSON object."""
        if not isinstance(self.section_data, dict):
            try:
                self.section_data = (
                    json.loads(self.section_data) if self.section_data else {}
                )
            except (ValueError, json.JSONDecodeError):
                self.section_data = {}

    def open_next(self):
        """Transition to the next state."""
        self._save_section_data()
        self._transition_state("next")
        self._load_section_data()
        return self._reopen_wizard()

    def open_previous(self):
        """Transition to the previous state."""
        self._save_section_data()
        self._transition_state("previous")
        self._load_section_data()
        return self._reopen_wizard()

    def _transition_state(self, direction):
        """Handle state transitions."""
        states = [state[0] for state in self._get_dynamic_states()]
        current_index = states.index(self.state)

        if direction == "next" and current_index < len(states) - 1:
            self.state = states[current_index + 1]
        elif direction == "previous" and current_index > 0:
            self.state = states[current_index - 1]
        else:
            raise ValidationError(_("No further state transitions possible."))

    def submit_wizard(self):
        """Submit the wizard data."""
        self._ensure_section_data()
        if not self.section_data:
            raise ValidationError(_("No section data available for submission."))
        self._finalize_submission()

    def _finalize_submission(self):
        """Finalize submission (override in child classes)."""
        raise NotImplementedError("Submission logic must be implemented in subclass.")

    def _save_section_data(self):
        """Save current section data (to be implemented in child classes)."""
        pass

    def _load_section_data(self):
        """Load saved section data (to be implemented in child classes)."""
        pass

    def _reopen_wizard(self):
        """Reopen the wizard."""
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def clear_section(self):
        """Clear current section data."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    def clear_all(self):
        """Clear all sections and reset the wizard."""
        raise NotImplementedError("This method should be implemented in subclasses.")
