from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from odoo.addons.prescription_sale.tests.test_prescription_sale import TestPrescriptionSaleBase


class TestPrescriptionSaleMrp(TestPrescriptionSaleBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_kit = cls.product_product.create(
            {"name": "Product test 1", "type": "consu"}
        )
        cls.product_kit_comp_1 = cls.product_1
        cls.product_kit_comp_2 = cls.product_2
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_kit.id,
                "product_tmpl_id": cls.product_kit.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.product_kit_comp_1.id, "product_qty": 2},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.product_kit_comp_2.id, "product_qty": 4},
                    ),
                ],
            }
        )
        cls.product_2 = cls.product_product.create(
            {"name": "Product test 2", "type": "product"}
        )

        cls.sale_order = cls._create_sale_order(cls, [[cls.product_kit, 5]])
        cls.sale_order.action_confirm()
        # Maybe other modules create additional lines in the create
        # method in sale.order model, so let's find the correct line.
        cls.order_line = cls.sale_order.order_line.filtered(
            lambda r: r.product_id == cls.product_kit
        )
        cls.order_out_picking = cls.sale_order.picking_ids
        # Confirm but leave a backorder to split moves so we can test that
        # the wizard correctly creates the Prescription with the proper quantities
        for line in cls.order_out_picking.move_ids:
            line.quantity_done = line.product_uom_qty - 7
        wiz_act = cls.order_out_picking.button_validate()
        wiz = Form(
            cls.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()
        cls.backorder = cls.sale_order.picking_ids - cls.order_out_picking
        for line in cls.backorder.move_ids:
            line.quantity_done = line.product_uom_qty
        cls.backorder.button_validate()

    def test_create_prescription_from_so(self):
        order = self.sale_order
        out_pickings = self.order_out_picking + self.backorder
        wizard = self._prescription_sale_wizard(order)
        wizard.line_ids.quantity = 4
        res = wizard.create_and_open_prescription()
        prescription = self.env["prescription"].search(res["domain"])
        for prescription in prescription:
            self.assertEqual(prescription.partner_id, order.partner_id)
            self.assertEqual(prescription.order_id, order)
            self.assertTrue(prescription.picking_id in out_pickings)
        self.assertEqual(prescription.mapped("phantom_bom_product"), self.product_kit)
        self.assertEqual(
            prescription.mapped("product_id"), self.product_kit_comp_1 + self.product_kit_comp_2
        )
        prescription_1 = prescription.filtered(lambda x: x.product_id == self.product_kit_comp_1)
        prescription_2 = prescription.filtered(lambda x: x.product_id == self.product_kit_comp_2)
        move_1 = out_pickings.mapped("move_ids").filtered(
            lambda x: x.product_id == self.product_kit_comp_1
        )
        move_2 = out_pickings.mapped("move_ids").filtered(
            lambda x: x.product_id == self.product_kit_comp_2
        )
        self.assertEqual(sum(prescription_1.mapped("product_uom_qty")), 8)
        self.assertEqual(prescription_1.mapped("product_uom"), move_1.mapped("product_uom"))
        self.assertEqual(sum(prescription_2.mapped("product_uom_qty")), 16)
        self.assertEqual(prescription_2.mapped("product_uom"), move_2.mapped("product_uom"))
        self.assertEqual(prescription.state, "confirmed")
        self.assertEqual(
            prescription_1.mapped("reception_move_id.origin_returned_move_id"),
            move_1,
        )
        self.assertEqual(
            prescription_2.mapped("reception_move_id.origin_returned_move_id"),
            move_2,
        )
        self.assertEqual(
            prescription.mapped("reception_move_id.picking_id")
            + self.order_out_picking
            + self.backorder,
            order.picking_ids,
        )
        # Refund the Prescription
        user = self.env["res.users"].create(
            {"login": "test_refund_with_so", "name": "Test"}
        )
        order.user_id = user.id
        prescription.reception_move_id.quantity_done = prescription.product_uom_qty
        prescription.reception_move_id.picking_id._action_done()
        # All the component Prescription must be received if we want to make a refund
        with self.assertRaises(UserError):
            prescription.action_refund()
        prescription_left = prescription - prescription
        for additional_prescription in prescription_left:
            additional_prescription.reception_move_id.quantity_done = (
                additional_prescription.product_uom_qty
            )
            additional_prescription.reception_move_id.picking_id._action_done()
        prescription.action_refund()
        self.assertEqual(prescription.refund_id.user_id, user)
        # The component Prescription get automatically refunded
        self.assertEqual(prescription.refund_id, prescription_left.mapped("refund_id"))
        # The refund product is the kit, not the components
        self.assertEqual(prescription.refund_id.invoice_line_ids.product_id, self.product_kit)
        prescription.refund_id.action_post()
        # We can still return another kit
        wizard_id = order.action_create_prescription()["res_id"]
        wizard = self.env["sale.order.prescription.wizard"].browse(wizard_id)
        self.assertEqual(wizard.line_ids.quantity, 1)
        wizard.create_and_open_prescription()
        # Now we open the wizard again and try to force the Prescription qty wich should
        # be 0 at this time
        wizard_id = order.action_create_prescription()["res_id"]
        wizard = self.env["sale.order.prescription.wizard"].browse(wizard_id)
        self.assertEqual(wizard.line_ids.quantity, 0)
        wizard.line_ids.quantity = 1
        with self.assertRaises(ValidationError):
            wizard.create_and_open_prescription()

    def test_report_prescription(self):
        wizard = self._prescription_sale_wizard(self.sale_order)
        wizard.line_ids.quantity = 4
        res = wizard.create_and_open_prescription()
        prescription = self.env["prescription"].search(res["domain"])
        for prescription in prescription:
            res = self.env["ir.actions.report"]._render_qweb_html(
                "prescription.report_prescription", prescription.ids
            )
            self.assertRegex(str(res[0]), self.product_kit_comp_1.name)
            self.assertRegex(str(res[0]), self.product_kit_comp_2.name)
