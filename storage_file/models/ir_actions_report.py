from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def render_qweb_pdf(self, res_ids=None, data=None):
        return super(
            IrActionsReport, self.with_context(print_report_pdf=True)
        ).render_qweb_pdf(res_ids=res_ids, data=data)
