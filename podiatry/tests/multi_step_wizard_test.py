# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MultiStepWizardTest(models.TransientModel):
    _name = "prescription.wizard.test"
    _description = "Multi Step Wizard Test"
    _inherit = "prescription.wizard.mixin"

    def state_previous_final(self):
        self.write({"state": "start"})
