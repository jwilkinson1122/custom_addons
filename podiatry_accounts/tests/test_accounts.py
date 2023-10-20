# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests import common


class TestAccounts(common.TransactionCase):
    def setUp(self):
        super(TestAccounts, self).setUp()
        self.payslip_line_obj = self.env["patient.payslip.line"]
        self.accounts_structure_line_obj = self.env["patient.accounts.structure.line"]
        self.accounts_register_obj = self.env["patient.accounts.register"]
        self.accounts_structure_obj = self.env["patient.accounts.structure"]
        self.patient_payslip_obj = self.env["patient.payslip"]
        self.patient = self.env.ref("podiatry.demo_patient_patient_6")
        self.podiatry = self.env.ref("podiatry.demo_podiatry_1")
        self.standard = self.env.ref("podiatry.demo_podiatry_standard_1")
        self.product = self.env.ref("podiatry_accounts.demo_product_accounts_1")
        #       Create Payslip Line
        self.payslip_line = self.payslip_line_obj.create(
            {
                "name": "Test case-accounts",
                "code": "10",
                "type": "month",
                "amount": 2000.00,
                "product_id": self.product.id,
            }
        )
        #       Create Accounts_structure_line
        self.accounts_structure_line = self.accounts_structure_line_obj.create(
            {
                "name": "Podiatry Accounts",
                "code": "01",
                "type": "month",
                "amount": 4000.00,
                "product_id": self.product.id,
            }
        )
        #        Create accounts structure
        self.accounts_structure = self.accounts_structure_obj.create(
            {
                "name": "accounts structure-2017",
                "code": "FS-2017",
                "line_ids": [(4, self.accounts_structure_line.id)],
            }
        )
        #        find the sale type journal
        self.journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        # Create Patient Accounts Register
        self.accounts_register = self.accounts_register_obj.create(
            {
                "name": self.patient.id,
                "date": "2017-06-05",
                "company_id": self.podiatry.company_id.id,
                "accounts_structure": self.accounts_structure.id,
                "standard_id": self.standard.id,
                "journal_id": self.journal.id,
            }
        )
        self.accounts_register._compute_total_amount()
        self.accounts_register.accounts_register_draft()
        self.accounts_register.accounts_register_confirm()
        #        Create Patient Accounts Receipt
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.patient_payslip = self.patient_payslip_obj.create(
            {
                "patient_id": self.patient.id,
                "name": "Test Accounts Receipt",
                "number": "SLIP/097",
                "date": current_date,
                "accounts_structure_id": self.accounts_structure.id,
                "journal_id": self.journal.id,
            }
        )
        self.patient_payslip.onchange_patient()
        self.patient_payslip.onchange_journal_id()
        self.patient_payslip.payslip_confirm()
        self.patient_payslip.patient_pay_accounts()
        self.patient_payslip.payslip_paid()
        self.patient_payslip.invoice_view()

    def test_accounts(self):
        self.assertEqual(self.patient.state, "done")
