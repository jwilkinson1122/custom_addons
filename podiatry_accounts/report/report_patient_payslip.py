# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportPatientPayslip(models.AbstractModel):
    _name = "report.podiatry_accounts.patient_payslip"
    _description = "Podiatry Accounts Payslip Report"

    def get_month(self, indate):
        """Method to get month"""
        out_date = indate.strftime("%B") + "-" + indate.strftime("%Y")
        return out_date

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report data"""
        patient_payslip_rec = self.env["patient.payslip"].search(
            [("id", "in", docids)]
        )
        payslip_model = self.env["ir.actions.report"]._get_report_from_name(
            "podiatry_accounts.patient_payslip"
        )
        return {
            "doc_ids": docids,
            "doc_model": payslip_model.model,
            "docs": patient_payslip_rec,
            "data": data,
            "get_month": self.get_month,
        }
