from odoo.tests.common import tagged
from odoo.addons.account_journal_inter_company.tests import common


@tagged("post_install", "-at_install")
class TestInterCompanyCashInvoice(common.TestInterCompany):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "service", "company_id": False}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner", "company_id": False}
        )

    def test_cash_invoice(self):
        self.create_inter_company(self.company_1, self.company_2)
        journal_1 = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company_1.id),
                ("type", "in", ["cash", "bank"]),
            ],
            limit=1,
        )
        statement = self.env["account.bank.statement"].create(
            {
                "name": "Statement",
                "journal_id": journal_1.id,
                "company_id": journal_1.company_id.id,
            }
        )
        invoice_out = self.create_invoice(
            self.company_2, "out_invoice", self.partner, self.product
        )
        invoice_in = self.create_invoice(
            self.company_2, "in_invoice", self.partner, self.product
        )
        in_invoice = (
            self.env["cash.invoice.in"]
            .with_context(active_ids=statement.ids, active_model=statement._name)
            .create({"invoice_id": invoice_in.id, "amount": -100.0})
        )
        in_invoice.run()
        out_invoice = (
            self.env["cash.invoice.out"]
            .with_context(active_ids=statement.ids, active_model=statement._name)
            .create({"invoice_id": invoice_out.id, "amount": 100.0})
        )
        out_invoice.run()
        statement.balance_end_real = statement.balance_start
        statement.button_post()
        invoice_out.refresh()
        invoice_in.refresh()
        self.assertEqual(invoice_in.amount_residual, 0.0)
        self.assertEqual(invoice_out.amount_residual, 0.0)
