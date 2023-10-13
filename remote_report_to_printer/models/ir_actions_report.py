from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _get_user_default_print_behaviour(self):
        res = super()._get_user_default_print_behaviour()
        if res.get("action", "unknown") == "remote_default":
            res.update(self.remote.get_printer_behaviour())
        return res

    def _get_report_default_print_behaviour(self):
        res = super()._get_report_default_print_behaviour()
        if res.get("action", "unknown") == "remote_default":
            res.update(self.remote.get_printer_behaviour())
        return res
