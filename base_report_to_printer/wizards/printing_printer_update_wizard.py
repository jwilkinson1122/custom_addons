import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PrintingPrinterUpdateWizard(models.TransientModel):
    _name = "printing.printer.update.wizard"
    _description = "Printing Printer Update Wizard"

    def action_ok(self):
        self.env["printing.server"].search([]).update_printers(raise_on_error=True)

        return {
            "name": "Printers",
            "view_mode": "tree,form",
            "res_model": "printing.printer",
            "type": "ir.actions.act_window",
            "target": "current",
        }
