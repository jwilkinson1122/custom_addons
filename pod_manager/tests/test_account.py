# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests import common


class TestAccount(common.TransactionCase):
    def setUp(self):
        super(TestAccount, self).setUp()

        self.account_prescription_obj = self.env["account.prescription"]
        self.account_prescription_line = self.env["account.prescription.line"]
        self.warehouse = self.env.ref("stock.warehouse0")
        self.partner = self.env.ref("base.res_partner_2")
        self.price_list = self.env.ref("product.list0")
        self.device = self.env.ref("pod_manager.account_device_0")
        cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.account_prescription = self.account_prescription_obj.create(
            {
                "name": "Prescription/00001",
                "date_order": cur_date,
                "warehouse_id": self.warehouse.id,
                "invoice_status": "no",
                "pricelist_id": self.price_list.id,
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "state": "draft",
            }
        )

    def test_confirm_sale(self):
        self.account_prescription.action_confirm()
        self.assertEqual(self.account_prescription.state == "sale", True)

    def test_prescription_cancel(self):
        self.account_prescription.action_cancel()
        self.assertEqual(self.account_prescription.state == "cancel", True)

    def test_prescription_set_to_draft(self):
        self.account_prescription.action_cancel_draft()
        self.assertEqual(self.account_prescription.state == "draft", True)

    def test_set_done(self):
        self.account_prescription.action_done()
        self.assertEqual(self.account_prescription.state == "done", True)
