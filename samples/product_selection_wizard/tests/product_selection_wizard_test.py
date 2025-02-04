from odoo import models


class ProductSelectionWizardTest(models.TransientModel):
    _name = "product.selection.wizard.test"
    _description = "Product Selection Wizard Test"
    _inherit = "product.selection.wizard.mixin"

    def state_previous_final(self):
        self.write({"state": "start"})
