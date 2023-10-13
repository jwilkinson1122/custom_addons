import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MultiStepWizard(models.AbstractModel):
    _name = "create.prescription.product"
    _name = "multi.step.wizard.mixin"
    _description = "Multi Steps Wizard Mixin"

    state = fields.Selection(selection="_selection_state", default="start", required=True)
    allow_back = fields.Boolean(compute="_compute_allow_back")

    @api.depends("state")
    def _compute_allow_back(self):
        """_selection_state must return 
        all possible step of the wizard. """
        for record in self:
            record.allow_back = getattr(
                record, "state_previous_%s" % record.state, False
            )

    @api.model
    def _selection_state(self):
        """ For each state but final, there must be a method named "state_exit_X"
        where X is the name of the state. Each of these method must set the next 
        state in self.state.
        
        For each state but start, there may be a method named "state_previous_X" 
        where X is the name of the state. Each of these method must set the next 
        state in self.state.
        
        The final state has no related method because the view should only 
        display a button to close the wizard."""
        
        return [("start", "Start"), ("final", "Final")]

    def open_next(self):
        """ open_next, open_previous and _reopen_self should not need to be
        overidden, but _selection_state and state_exit_start likely will need to."""
        state_method = getattr(self, "state_exit_{}".format(self.state), None)
        if state_method is None:
            raise NotImplementedError(
                "No method defined for state {}".format(self.state)
            )
        state_method()
        return self._reopen_self()

    def open_previous(self):
        state_method = getattr(self, "state_previous_{}".format(self.state), None)
        if state_method is None:
            raise NotImplementedError(
                "No method defined for state {}".format(self.state)
            )
        state_method()
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def state_exit_start(self):
        self.state = "final"