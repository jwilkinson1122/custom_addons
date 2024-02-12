from odoo.tests import Form, TransactionCase
from odoo.tests.common import users


class TestPrescriptionSaleBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_partner = cls.env["res.partner"]
        cls.product_product = cls.env["product.product"]
        cls.so_model = cls.env["sale.order"]

        cls.product_1 = cls.product_product.create(
            {"name": "Product test 1", "type": "product"}
        )
        cls.product_2 = cls.product_product.create(
            {"name": "Product test 2", "type": "product"}
        )
        cls.partner = cls.res_partner.create(
            {"name": "Partner test", "email": "partner@prescription"}
        )
        cls.report_model = cls.env["ir.actions.report"]
        cls.prescription_operation_model = cls.env["prescription.operation"]
        cls._partner_portal_wizard(cls, cls.partner)

    def _create_sale_order(self, products):
        order_form = Form(self.so_model)
        order_form.partner_id = self.partner
        for product_info in products:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product_info[0]
                line_form.product_uom_qty = product_info[1]
        return order_form.save()

    def _partner_portal_wizard(self, partner):
        wizard_all = (
            self.env["portal.wizard"]
            .with_context(**{"active_ids": [partner.id]})
            .create({})
        )
        wizard_all.user_ids.action_grant_access()

    def _prescription_sale_wizard(self, order):
        wizard_id = order.action_create_prescription()["res_id"]
        return self.env["sale.order.prescription.wizard"].browse(wizard_id)


class TestPrescriptionSale(TestPrescriptionSaleBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls._create_sale_order(cls, [[cls.product_1, 5]])
        cls.sale_order.action_confirm()
        # Maybe other modules create additional lines in the create
        # method in sale.order model, so let's find the correct line.
        cls.order_line = cls.sale_order.order_line.filtered(
            lambda r: r.product_id == cls.product_1
        )
        cls.order_out_picking = cls.sale_order.picking_ids
        cls.order_out_picking.move_ids.quantity_done = 5
        cls.order_out_picking.button_validate()

    def test_prescription_sale_computes_onchange(self):
        prescription = self.env["prescription"].new()
        # No m2m values when everything is selectable
        self.assertFalse(prescription.allowed_picking_ids)
        self.assertFalse(prescription.allowed_move_ids)
        self.assertFalse(prescription.allowed_product_ids)
        # Partner selected
        prescription.order_id = self.sale_order
        prescription.partner_id = self.partner
        self.assertFalse(prescription.order_id)
        self.assertEqual(prescription.allowed_picking_ids._origin, self.order_out_picking)
        # Order selected
        prescription.order_id = self.sale_order
        self.assertEqual(prescription.allowed_picking_ids._origin, self.order_out_picking)
        prescription.picking_id = self.order_out_picking
        self.assertEqual(prescription.allowed_move_ids._origin, self.order_out_picking.move_ids)
        self.assertEqual(prescription.allowed_product_ids._origin, self.product_1)
        # Onchanges
        prescription.product_id = self.product_1
        prescription._onchange_order_id()
        self.assertFalse(prescription.product_id)
        self.assertFalse(prescription.picking_id)

    def test_create_prescription_with_so(self):
        prescription_vals = {
            "partner_id": self.partner.id,
            "order_id": self.sale_order.id,
            "product_id": self.product_1.id,
            "product_uom_qty": 5,
            "location_id": self.sale_order.warehouse_id.prescription_loc_id.id,
        }
        prescription = self.env["prescription"].create(prescription_vals)
        prescription.action_confirm()
        self.assertTrue(prescription.reception_move_id)
        self.assertFalse(prescription.reception_move_id.origin_returned_move_id)

    def test_create_prescription_from_so(self):
        order = self.sale_order
        wizard = self._prescription_sale_wizard(order)
        prescription = self.env["prescription"].browse(wizard.create_and_open_prescription()["res_id"])
        self.assertEqual(prescription.partner_id, order.partner_id)
        self.assertEqual(prescription.order_id, order)
        self.assertEqual(prescription.picking_id, self.order_out_picking)
        self.assertEqual(prescription.move_id, self.order_out_picking.move_ids)
        self.assertEqual(prescription.product_id, self.product_1)
        self.assertEqual(prescription.product_uom_qty, self.order_line.product_uom_qty)
        self.assertEqual(prescription.product_uom, self.order_line.product_uom)
        self.assertEqual(prescription.state, "confirmed")
        self.assertEqual(
            prescription.reception_move_id.origin_returned_move_id,
            self.order_out_picking.move_ids,
        )
        self.assertEqual(
            prescription.reception_move_id.picking_id + self.order_out_picking,
            order.picking_ids,
        )
        user = self.env["res.users"].create(
            {"login": "test_refund_with_so", "name": "Test"}
        )
        order.user_id = user.id
        # Receive the Prescription
        prescription.action_confirm()
        prescription.reception_move_id.quantity_done = prescription.product_uom_qty
        prescription.reception_move_id.picking_id._action_done()
        # Refund the Prescription
        prescription.action_refund()
        self.assertEqual(self.order_line.qty_delivered, 0)
        self.assertEqual(self.order_line.qty_invoiced, -5)
        self.assertEqual(prescription.refund_id.user_id, user)
        self.assertEqual(prescription.refund_id.invoice_line_ids.sale_line_ids, self.order_line)
        # Cancel the refund
        prescription.refund_id.button_cancel()
        self.assertEqual(self.order_line.qty_delivered, 5)
        self.assertEqual(self.order_line.qty_invoiced, 0)
        # And put it to draft again
        prescription.refund_id.button_draft()
        self.assertEqual(self.order_line.qty_delivered, 0)
        self.assertEqual(self.order_line.qty_invoiced, -5)

    @users("partner@prescription")
    def test_create_prescription_from_so_portal_user(self):
        order = self.sale_order
        wizard_obj = (
            self.env["sale.order.prescription.wizard"].sudo().with_context(active_id=order.id)
        )
        operation = self.prescription_operation_model.sudo().search([], limit=1)
        line_vals = [
            (
                0,
                0,
                {
                    "product_id": order.order_line.product_id.id,
                    "sale_line_id": order.order_line.id,
                    "quantity": order.order_line.product_uom_qty,
                    "uom_id": order.order_line.product_uom.id,
                    "picking_id": order.picking_ids[0].id,
                    "operation_id": operation.id,
                },
            )
        ]
        wizard = wizard_obj.create(
            {
                "line_ids": line_vals,
                "location_id": order.warehouse_id.prescription_loc_id.id,
            }
        )
        prescription = wizard.sudo().create_prescription(from_portal=True)
        self.assertEqual(prescription.order_id, order)
        self.assertIn(order.partner_id, prescription.message_partner_ids)
        self.assertEqual(order.prescription_count, 1)

    def test_create_recurrent_prescription(self):
        """An Prescription of a product that had an Prescription in the past should be possible"""
        wizard = self._prescription_sale_wizard(self.sale_order)
        prescription = self.env["prescription"].browse(wizard.create_and_open_prescription()["res_id"])
        prescription.reception_move_id.quantity_done = prescription.product_uom_qty
        prescription.reception_move_id.picking_id._action_done()
        wizard = self._prescription_sale_wizard(self.sale_order)
        self.assertEqual(
            wizard.line_ids.quantity,
            0,
            "There shouldn't be any allowed quantities for Prescriptions",
        )
        delivery_form = Form(
            self.env["prescription.delivery.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_delivery_type="return",
            )
        )
        delivery_form.product_uom_qty = prescription.product_uom_qty
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        picking = prescription.delivery_move_ids.picking_id
        picking.move_ids.quantity_done = prescription.product_uom_qty
        picking._action_done()
        # The product is returned to the customer, so we should be able to make
        # another Prescription in the future
        wizard = self._prescription_sale_wizard(self.sale_order)
        self.assertEqual(
            wizard.line_ids.quantity,
            prescription.product_uom_qty,
            "We should be allowed to return the product again",
        )

    def test_report_prescription(self):
        wizard = self._prescription_sale_wizard(self.sale_order)
        prescription = self.env["prescription"].browse(wizard.create_and_open_prescription()["res_id"])
        operation = self.prescription_operation_model.sudo().search([], limit=1)
        prescription.operation_id = operation.id
        res = self.env["ir.actions.report"]._render_qweb_html("prescription.report_prescription", prescription.ids)
        res = str(res[0])
        self.assertRegex(res, self.sale_order.name)
        self.assertRegex(res, operation.name)
