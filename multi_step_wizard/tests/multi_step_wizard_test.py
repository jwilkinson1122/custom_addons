from odoo import models


class MultiStepWizardTest(models.TransientModel):
    _name = "multi.step.wizard.test"
    _description = "Multi Step Wizard Test"
    _inherit = "multi.step.wizard.mixin"

    def state_previous_final(self):
        self.write({"state": "start"})
