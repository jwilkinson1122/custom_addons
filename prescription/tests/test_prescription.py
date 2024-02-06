# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests import common


class TestPrescription(common.TransactionCase):
    def setUp(self):
        super(TestPrescription, self).setUp()

        self.prescription_order_obj = self.env["prescription.order"]
        self.prescription_order_line = self.env["prescription.order.line"]
        self.warehouse = self.env.ref("stock.warehouse0")
        self.partner = self.env.ref("base.res_partner_2")
        self.price_list = self.env.ref("product.list0")
        self.device = self.env.ref("prescription.prescription_device_1")
        cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.prescription_order = self.prescription_order_obj.create(
            {
                "name": "Order/00001",
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
        self.prescription_order.action_confirm()
        self.assertEqual(self.prescription_order.state == "sale", True)

    def test_order_cancel(self):
        self.prescription_order.action_cancel()
        self.assertEqual(self.prescription_order.state == "cancel", True)

    def test_order_set_to_draft(self):
        self.prescription_order.action_cancel_draft()
        self.assertEqual(self.prescription_order.state == "draft", True)

    def test_set_done(self):
        self.prescription_order.action_done()
        self.assertEqual(self.prescription_order.state == "done", True)
