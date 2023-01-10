# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PrescriptionReportWizard(models.TransientModel):
    _name = "prescription.report.wizard"
    _rec_name = "date_start"
    _description = "Allow print prescription report by date"

    date_start = fields.Datetime("Start Date")
    date_end = fields.Datetime("End Date")

    def print_report(self):
        data = {
            "ids": self.ids,
            "model": "podiatry.prescription",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("pod_erp.report_podiatry_management").report_action(
            self, data=data
        )
