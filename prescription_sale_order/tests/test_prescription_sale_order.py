from odoo.tests.common import TransactionCase


class TestPrescriptionSaleOrder(TransactionCase):
    def setUp(self):
        super(TestPrescriptionSaleOrder, self).setUp()

        self.prescription_type = self.env["prescription.type"].create(
            {
                "name": "Desk leg spare order",
                "create_sale_order": True,
            }
        )

        self.product1 = self.env["product.product"].create(
            {
                "name": "Test product",
                "standard_price": 10,
                "list_price": 20,
            }
        )

        self.product2 = self.env["product.product"].create(
            {
                "name": "Test product 2",
                "standard_price": 5,
                "list_price": 15,
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "partner_a",
                "company_id": False,
            }
        )

        self.prescription_rx1 = self.env["prescription.order"].create(
            {
                "name": "Test",
                "product_id": self.product1.id,
                "partner_id": self.partner.id,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "prescription_type_id": self.prescription_type.id,
            }
        )

        self.line = self.env["prescription.line"].create(
            {
                "name": self.product2.name,
                "prescription_id": self.prescription_rx1.id,
                "price_unit": 2.0,
                "product_id": self.product2.id,
                "product_uom_qty": 1.0,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "location_dest_id": self.env.ref(
                    "product.product_product_3"
                ).property_stock_production.id,
                "company_id": self.env.company.id,
            }
        )

        self.prescription_rx1.operations |= self.line

    def test_prescription_sale_order(self):
        self.prescription_rx1.action_validate()
        action = self.prescription_rx1.action_create_sale_order()
        self.sale_order = self.env["sale.order"].browse(action["res_id"])
        self.sale_order.action_confirm()
        self.move = self.sale_order._create_invoices()
        self.move.action_post()
