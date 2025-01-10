import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductSelectionWizardMixin(models.AbstractModel):
    _name = "product.selection.wizard.mixin"
    _description = "Product Selection Wizard Mixin"

    state = fields.Selection(
        selection="_selection_state", default="shell_foundation", required=True
    )
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

    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            record.allow_back = hasattr(record, f"state_previous_{record.state}")

    def _ensure_section_data(self):
        if not isinstance(self.section_data, dict):
            try:
                self.section_data = (
                    json.loads(self.section_data) if self.section_data else {}
                )
            except (ValueError, json.JSONDecodeError):
                self.section_data = {}

    def open_next(self):
        self._ensure_section_data()
        self._handle_state_transition("next")
        return self._reopen_wizard()

    def open_previous(self):
        self._ensure_section_data()
        self._handle_state_transition("previous")
        return self._reopen_wizard()

    def _handle_state_transition(self, direction):
        method_name = f"state_{direction}_{self.state}"
        if not hasattr(self, method_name):
            raise NotImplementedError(
                f"No method defined for state transition: {method_name}"
            )
        getattr(self, method_name)()

    def submit_wizard(self):
        if not self.section_data:
            raise ValidationError("No section data available for submission.")
        self._finalize_submission()

    def _finalize_submission(self):
        raise NotImplementedError("Submission logic must be implemented in subclass")

    def _reopen_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
