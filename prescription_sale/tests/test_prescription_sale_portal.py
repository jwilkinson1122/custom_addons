from markupsafe import Markup

from odoo import Command
from odoo.tests import HttpCase, tagged

from .test_prescription_sale import TestPrescriptionSaleBase


@tagged("-at-install", "post-install")
class TestPrescriptionSalePortal(TestPrescriptionSaleBase, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls._create_sale_order(cls, [[cls.product_1, 5]])
        # So we can click it in the tour
        cls.sale_order.name = "Test Sale Prescription SO"
        cls.sale_order.action_confirm()
        # Maybe other modules create additional lines in the create
        # method in sale.order model, so let's find the correct line.
        cls.order_line = cls.sale_order.order_line.filtered(
            lambda r: r.product_id == cls.product_1
        )
        cls.order_out_picking = cls.sale_order.picking_ids
        cls.order_out_picking.move_ids.quantity_done = 5
        cls.order_out_picking.button_validate()
        # Let's create some companion contacts
        cls.partner_company = cls.res_partner.create(
            {"name": "Partner test Co", "email": "partner_co@test.com"}
        )
        cls.another_partner = cls.res_partner.create(
            {
                "name": "Another address",
                "email": "another_partner@test.com",
                "parent_id": cls.partner_company.id,
            }
        )
        cls.partner.parent_id = cls.partner_company
        # Create our portal user
        cls.user_portal = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": "prescription_portal",
                    "password": "prescription_portal",
                    "partner_id": cls.partner.id,
                    "groups_id": [Command.set([cls.env.ref("base.group_portal").id])],
                }
            )
        )

    def test_prescription_sale_portal(self):
        self.start_tour("/", "prescription_sale_portal", login="prescription_portal")
        prescription = self.sale_order.prescription_ids
        # Check that the portal values are properly transmited
        self.assertEqual(prescription.state, "draft")
        self.assertEqual(prescription.partner_id, self.partner)
        self.assertEqual(prescription.partner_shipping_id, self.another_partner)
        self.assertEqual(prescription.product_uom_qty, 1)
        self.assertEqual(
            prescription.description, Markup("<p>I'd like to change this product</p>")
        )
