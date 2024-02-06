# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OrderReportWizard(models.TransientModel):
    _name = "order.report.wizard"
    _rec_name = "date_start"
    _description = "Allow print order report by date"

    date_start = fields.Datetime("Start Date")
    date_end = fields.Datetime("End Date")

    def print_report(self):
        data = {
            "ids": self.ids,
            "model": "prescription.order",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("prescription.report_prescription_management").report_action(
            self, data=data
        )
