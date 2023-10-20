# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportPatientAccountsRegister(models.AbstractModel):
    _name = "report.podiatry_accounts.patient_accounts_register"
    _description = "Podiatry Accounts Register Report"

    def get_month(self, indate):
        """Method to get month"""
        return indate.strftime("%B") + "-" + indate.strftime("%Y")

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report data"""
        patients_rec = self.env["patient.accounts.register"].search(
            [("id", "in", docids)]
        )
        accounts_report = self.env["ir.actions.report"]._get_report_from_name(
            "podiatry_accounts.patient_accounts_register"
        )
        return {
            "doc_ids": docids,
            "doc_model": accounts_report.model,
            "docs": patients_rec,
            "data": data,
            "get_month": self.get_month,
        }
