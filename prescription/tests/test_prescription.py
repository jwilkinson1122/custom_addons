# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests import Form, TransactionCase, new_test_user, users, common
from odoo.exceptions import UserError, ValidationError



class TestPrescription(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.user_prescription = new_test_user(
            cls.env,
            login="user_prescription",
            groups="prescription_contacts.group_contacts_user,stock.group_stock_user",
        )
        cls.res_partner = cls.env["res.partner"]
        cls.product_product = cls.env["product.product"]
        cls.company = cls.env.user.company_id
        cls.warehouse_company = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.prescription_loc = cls.warehouse_company.prescription_loc_id
        cls.product = cls.product_product.create(
            {"name": "Product test 1", "type": "product"}
        )
        cls.account_receiv = cls.env["account.account"].create(
            {
                "name": "Receivable",
                "code": "RCV00",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.partner = cls.res_partner.create(
            {
                "name": "Partner test",
                "property_account_receivable_id": cls.account_receiv.id,
                "property_payment_term_id": cls.env.ref(
                    "account.account_payment_term_30days"
                ).id,
            }
        )
        cls.partner_invoice = cls.res_partner.create(
            {
                "name": "Partner invoice test",
                "parent_id": cls.partner.id,
                "type": "invoice",
            }
        )
        cls.partner_shipping = cls.res_partner.create(
            {
                "name": "Partner shipping test",
                "parent_id": cls.partner.id,
                "type": "delivery",
            }
        )
        cls.finalization_reason_1 = cls.env["prescription.finalization"].create(
            {"name": ("[Test] It can't be prescriptioned and customer doesn't want it")}
        )
        cls.finalization_reason_2 = cls.env["prescription.finalization"].create(
            {"name": "[Test] It's out of warranty. To be scrapped"}
        )
        cls.env.ref("prescription.group_prescription_manual_finalization").users |= cls.env.user
        # Ensure grouping
        cls.env.company.prescription_return_grouping = True

    def _create_prescription(self, partner=None, product=None, qty=None, location=None):
        vals = {}
        if partner:
            vals["partner_id"] = partner.id
        if product:
            vals["product_id"] = product.id
        if qty:
            vals["product_uom_qty"] = qty
        if location:
            vals["location_id"] = location.id
        return self.env["prescription"].create(vals)

    def _create_confirm_receive(
        self, partner=None, product=None, qty=None, location=None
    ):
        prescription = self._create_prescription(partner, product, qty, location)
        prescription.action_confirm()
        prescription.reception_move_id.quantity_done = prescription.product_uom_qty
        prescription.reception_move_id.picking_id._action_done()
        return prescription

    def _create_delivery(self):
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "outgoing"),
                "|",
                ("warehouse_id.company_id", "=", self.company.id),
                ("warehouse_id", "=", False),
            ],
            limit=1,
        )
        picking_form = Form(
            recordp=self.env["stock.picking"].with_context(
                default_picking_type_id=picking_type.id
            ),
            view="stock.view_picking_form",
        )
        picking_form.partner_id = self.partner
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 10
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product_product.create(
                {"name": "Product 2 test", "type": "product"}
            )
            move.product_uom_qty = 20
        picking = picking_form.save()
        picking.action_confirm()
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        return picking

    
    def setUp(self):
        super(TestPrescription, self).setUp()
        self.prescription_obj = self.env["prescription"]
        self.prescription_line = self.env["prescription.line"]
        self.warehouse = self.env.ref("stock.warehouse0")
        self.partner = self.env.ref("base.res_partner_2")
        self.price_list = self.env.ref("product.list0")
        self.device = self.env.ref("prescription.prescription_device_1")
        cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.prescription = self.prescription_obj.create(
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
        self.prescription.action_confirm()
        self.assertEqual(self.prescription.state == "sale", True)

    def test_order_cancel(self):
        self.prescription.action_cancel()
        self.assertEqual(self.prescription.state == "cancel", True)

    def test_order_set_to_draft(self):
        self.prescription.action_cancel_draft()
        self.assertEqual(self.prescription.state == "draft", True)

    def test_set_done(self):
        self.prescription.action_done()
        self.assertEqual(self.prescription.state == "done", True)


class TestPrescriptionCase(TestPrescription):
    def test_computed(self):
        # If partner changes, the invoice address is set
        prescription = self.env["prescription"].new()
        prescription.partner_id = self.partner
        self.assertEqual(prescription.partner_invoice_id, self.partner_invoice)
        # If origin move changes, the product is set
        uom_ten = self.env["uom.uom"].create(
            {
                "name": "Ten",
                "category_id": self.env.ref("uom.product_uom_unit").id,
                "factor_inv": 10,
                "uom_type": "bigger",
            }
        )
        product_2 = self.product_product.create(
            {"name": "Product test 2", "type": "product", "uom_id": uom_ten.id}
        )
        outgoing_picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "outgoing"),
                "|",
                ("warehouse_id.company_id", "=", self.company.id),
                ("warehouse_id", "=", False),
            ],
            limit=1,
        )
        picking_form = Form(
            recordp=self.env["stock.picking"].with_context(
                default_picking_type_id=outgoing_picking_type.id
            ),
            view="stock.view_picking_form",
        )
        picking_form.partner_id = self.partner
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = product_2
            move.product_uom_qty = 15
        picking = picking_form.save()
        picking._action_done()
        prescription.picking_id = picking
        prescription.move_id = picking.move_ids
        self.assertEqual(prescription.product_id, product_2)
        self.assertEqual(prescription.product_uom_qty, 15)
        self.assertEqual(prescription.product_uom, uom_ten)
        # If product changes, unit of measure changes
        prescription.move_id = False
        prescription.product_id = self.product
        self.assertEqual(prescription.product_uom, self.product.uom_id)

    def test_ensure_required_fields_on_confirm(self):
        prescription = self._create_prescription()
        with self.assertRaises(ValidationError) as e:
            prescription.action_confirm()
        self.assertEqual(
            e.exception.args[0],
            "Required field(s):\nCustomer\nShipping Address\nInvoice Address\nProduct",
        )
        prescription.partner_id = self.partner.id
        with self.assertRaises(ValidationError) as e:
            prescription.action_confirm()
        self.assertEqual(e.exception.args[0], "Required field(s):\nProduct")
        prescription.product_id = self.product.id
        prescription.location_id = self.prescription_loc.id
        prescription.action_confirm()
        self.assertEqual(prescription.state, "confirmed")

    def test_confirm_and_receive(self):
        prescription = self._create_prescription(self.partner, self.product, 10, self.prescription_loc)
        prescription.action_confirm()
        self.assertEqual(prescription.reception_move_id.picking_id.state, "assigned")
        self.assertEqual(prescription.reception_move_id.product_id, prescription.product_id)
        self.assertEqual(prescription.reception_move_id.product_uom_qty, 10)
        self.assertEqual(prescription.reception_move_id.product_uom, prescription.product_uom)
        self.assertEqual(prescription.state, "confirmed")
        prescription.reception_move_id.quantity_done = 9
        with self.assertRaises(ValidationError):
            prescription.reception_move_id.picking_id._action_done()
        prescription.reception_move_id.quantity_done = 10
        prescription.reception_move_id.picking_id._action_done()
        self.assertEqual(prescription.reception_move_id.picking_id.state, "done")
        self.assertEqual(prescription.reception_move_id.quantity_done, 10)
        self.assertEqual(prescription.state, "received")

    def test_cancel(self):
        # cancel a draft Prescription
        prescription = self._create_prescription(self.partner, self.product)
        prescription.action_cancel()
        self.assertEqual(prescription.state, "cancelled")
        # cancel a confirmed Prescription
        prescription = self._create_prescription(self.partner, self.product, 10, self.prescription_loc)
        prescription.action_confirm()
        prescription.action_cancel()
        self.assertEqual(prescription.state, "cancelled")
        # A Prescription is only cancelled from draft and confirmed states
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        with self.assertRaises(UserError):
            prescription.action_cancel()

    def test_lock_unlock(self):
        # A Prescription is only locked from 'received' state
        prescription_1 = self._create_prescription(self.partner, self.product, 10, self.prescription_loc)
        prescription_2 = self._create_confirm_receive(
            self.partner, self.product, 10, self.prescription_loc
        )
        self.assertEqual(prescription_1.state, "draft")
        self.assertEqual(prescription_2.state, "received")
        (prescription_1 | prescription_2).action_lock()
        self.assertEqual(prescription_1.state, "draft")
        self.assertEqual(prescription_2.state, "locked")
        # A Prescription is only unlocked from 'lock' state and it will be set
        # to 'received' state
        (prescription_1 | prescription_2).action_unlock()
        self.assertEqual(prescription_1.state, "draft")
        self.assertEqual(prescription_2.state, "received")

    @users("__system__", "user_prescription")
    def test_action_refund(self):
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        self.assertEqual(prescription.state, "received")
        self.assertTrue(prescription.can_be_refunded)
        self.assertTrue(prescription.can_be_returned)
        self.assertTrue(prescription.can_be_replaced)
        prescription.action_refund()
        self.assertEqual(prescription.refund_id.move_type, "out_refund")
        self.assertEqual(prescription.refund_id.state, "draft")
        self.assertFalse(prescription.refund_id.invoice_payment_term_id)
        self.assertEqual(prescription.refund_line_id.product_id, prescription.product_id)
        self.assertEqual(prescription.refund_line_id.quantity, 10)
        self.assertEqual(prescription.refund_line_id.product_uom_id, prescription.product_uom)
        self.assertEqual(prescription.state, "refunded")
        self.assertFalse(prescription.can_be_refunded)
        self.assertFalse(prescription.can_be_returned)
        self.assertFalse(prescription.can_be_replaced)
        # A regular user can create the refund but only Invoicing users will be able
        # to edit it and post it
        if self.env.user.login != "__system__":
            return
        with Form(prescription.refund_line_id.move_id) as refund_form:
            with refund_form.invoice_line_ids.edit(0) as refund_line:
                refund_line.quantity = 9
        with self.assertRaises(ValidationError):
            prescription.refund_id.action_post()
        with Form(prescription.refund_line_id.move_id) as refund_form:
            with refund_form.invoice_line_ids.edit(0) as refund_line:
                refund_line.quantity = 10
        prescription.refund_id.action_post()
        self.assertFalse(prescription.can_be_refunded)
        self.assertFalse(prescription.can_be_returned)
        self.assertFalse(prescription.can_be_replaced)

    def test_mass_refund(self):
        # Create, confirm and receive prescription_1
        prescription_1 = self._create_confirm_receive(
            self.partner, self.product, 10, self.prescription_loc
        )
        # create, confirm and receive 3 more Prescription
        # prescription_2: Same partner and same product as prescription_1
        prescription_2 = self._create_confirm_receive(
            self.partner, self.product, 15, self.prescription_loc
        )
        # prescription_3: Same partner and different product than prescription_1
        product = self.product_product.create(
            {"name": "Product 2 test", "type": "product"}
        )
        prescription_3 = self._create_confirm_receive(self.partner, product, 20, self.prescription_loc)
        # prescription_4: Different partner and same product as prescription_1
        partner = self.res_partner.create(
            {
                "name": "Partner 2 test",
                "property_account_receivable_id": self.account_receiv.id,
                "company_id": self.company.id,
            }
        )
        prescription_4 = self._create_confirm_receive(partner, product, 25, self.prescription_loc)
        # all prescription are ready to refund
        all_prescription = prescription_1 | prescription_2 | prescription_3 | prescription_4
        self.assertEqual(all_prescription.mapped("state"), ["received"] * 4)
        self.assertEqual(all_prescription.mapped("can_be_refunded"), [True] * 4)
        # Mass refund of those four Prescription
        action = self.env.ref("prescription.prescription_refund_action_server")
        ctx = dict(self.env.context)
        ctx.update(active_ids=all_prescription.ids, active_model="prescription")
        action.with_context(**ctx).run()
        # After that all Prescription are in 'refunded' state
        self.assertEqual(all_prescription.mapped("state"), ["refunded"] * 4)
        # Two refunds were created
        refund_1 = (prescription_1 | prescription_2 | prescription_3).mapped("refund_id")
        refund_2 = prescription_4.refund_id
        self.assertEqual(len(refund_1), 1)
        self.assertEqual(len(refund_2), 1)
        self.assertEqual((refund_1 | refund_2).mapped("state"), ["draft"] * 2)
        # One refund per partner
        self.assertNotEqual(refund_1.partner_id, refund_2.partner_id)
        self.assertEqual(
            refund_1.partner_id,
            (prescription_1 | prescription_2 | prescription_3).mapped("partner_invoice_id"),
        )
        self.assertEqual(refund_2.partner_id, prescription_4.partner_invoice_id)
        # Each Prescription (prescription_1, prescription_2 and prescription_3) is linked with a different
        # line of refund_1
        self.assertEqual(len(refund_1.invoice_line_ids), 3)
        self.assertEqual(
            refund_1.invoice_line_ids.mapped("prescription_id"),
            (prescription_1 | prescription_2 | prescription_3),
        )
        self.assertEqual(
            (prescription_1 | prescription_2 | prescription_3).mapped("refund_line_id"),
            refund_1.invoice_line_ids,
        )
        # prescription_4 is linked with the unique line of refund_2
        self.assertEqual(len(refund_2.invoice_line_ids), 1)
        self.assertEqual(refund_2.invoice_line_ids.prescription_id, prescription_4)
        self.assertEqual(prescription_4.refund_line_id, refund_2.invoice_line_ids)
        # Assert product and quantities are propagated correctly
        for prescription in all_prescription:
            self.assertEqual(prescription.product_id, prescription.refund_line_id.product_id)
            self.assertEqual(prescription.product_uom_qty, prescription.refund_line_id.quantity)
            self.assertEqual(prescription.product_uom, prescription.refund_line_id.product_uom_id)
        # Less quantity -> error on confirm
        with Form(prescription_2.refund_line_id.move_id) as refund_form:
            with refund_form.invoice_line_ids.edit(1) as refund_line:
                refund_line.quantity = 14
        with self.assertRaises(ValidationError):
            refund_1.action_post()
        with Form(prescription_2.refund_line_id.move_id) as refund_form:
            with refund_form.invoice_line_ids.edit(1) as refund_line:
                refund_line.quantity = 15
        refund_1.action_post()
        refund_2.action_post()

    def test_replace(self):
        # Create, confirm and receive an Prescription
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        # Replace with another product with quantity 2.
        product_2 = self.product_product.create(
            {"name": "Product 2 test", "type": "product"}
        )
        delivery_form = Form(
            self.env["prescription.delivery.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_delivery_type="replace",
            )
        )
        delivery_form.product_id = product_2
        delivery_form.product_uom_qty = 2
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        self.assertEqual(len(prescription.move_ids.picking_id.move_ids), 1)
        self.assertEqual(prescription.move_ids.product_id, product_2)
        self.assertEqual(prescription.move_ids.product_uom_qty, 2)
        self.assertTrue(prescription.move_ids.picking_id.state, "waiting")
        self.assertEqual(prescription.state, "waiting_replacement")
        self.assertFalse(prescription.can_be_refunded)
        self.assertFalse(prescription.can_be_returned)
        self.assertTrue(prescription.can_be_replaced)
        self.assertEqual(prescription.delivered_qty, 2)
        self.assertEqual(prescription.remaining_qty, 8)
        self.assertEqual(prescription.delivered_qty_done, 0)
        self.assertEqual(prescription.remaining_qty_to_done, 10)
        first_move = prescription.move_ids
        picking = first_move.picking_id
        # Replace again with another product with the remaining quantity
        product_3 = self.product_product.create(
            {"name": "Product 3 test", "type": "product"}
        )
        delivery_form = Form(
            self.env["prescription.delivery.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_delivery_type="replace",
            )
        )
        delivery_form.product_id = product_3
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        second_move = prescription.move_ids - first_move
        self.assertEqual(len(prescription.move_ids), 2)
        self.assertEqual(prescription.move_ids.mapped("picking_id"), picking)
        self.assertEqual(first_move.product_id, product_2)
        self.assertEqual(first_move.product_uom_qty, 2)
        self.assertEqual(second_move.product_id, product_3)
        self.assertEqual(second_move.product_uom_qty, 8)
        self.assertTrue(picking.state, "waiting")
        self.assertEqual(prescription.delivered_qty, 10)
        self.assertEqual(prescription.remaining_qty, 0)
        self.assertEqual(prescription.delivered_qty_done, 0)
        self.assertEqual(prescription.remaining_qty_to_done, 10)
        # remaining_qty is 0 but prescription is not set to 'replaced' until
        # remaining_qty_to_done is less than or equal to 0
        first_move.quantity_done = 2
        second_move.quantity_done = 8
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(prescription.delivered_qty, 10)
        self.assertEqual(prescription.remaining_qty, 0)
        self.assertEqual(prescription.delivered_qty_done, 10)
        self.assertEqual(prescription.remaining_qty_to_done, 0)
        # The Prescription is now in 'replaced' state
        self.assertEqual(prescription.state, "replaced")
        self.assertFalse(prescription.can_be_refunded)
        self.assertFalse(prescription.can_be_returned)
        # Despite being in 'replaced' state,
        # Prescription can still perform replacements.
        self.assertTrue(prescription.can_be_replaced)

    def test_return_to_customer(self):
        # Create, confirm and receive an Prescription
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        # Return the same product with quantity 2 to the customer.
        delivery_form = Form(
            self.env["prescription.delivery.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_delivery_type="return",
            )
        )
        delivery_form.product_uom_qty = 2
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        picking = prescription.move_ids.picking_id
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(prescription.move_ids.product_id, self.product)
        self.assertEqual(prescription.move_ids.product_uom_qty, 2)
        self.assertTrue(picking.state, "waiting")
        self.assertEqual(prescription.state, "waiting_return")
        self.assertFalse(prescription.can_be_refunded)
        self.assertFalse(prescription.can_be_replaced)
        self.assertTrue(prescription.can_be_returned)
        self.assertEqual(prescription.delivered_qty, 2)
        self.assertEqual(prescription.remaining_qty, 8)
        self.assertEqual(prescription.delivered_qty_done, 0)
        self.assertEqual(prescription.remaining_qty_to_done, 10)
        first_move = prescription.move_ids
        picking = first_move.picking_id
        # Validate the picking
        first_move.quantity_done = 2
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(prescription.delivered_qty, 2)
        self.assertEqual(prescription.remaining_qty, 8)
        self.assertEqual(prescription.delivered_qty_done, 2)
        self.assertEqual(prescription.remaining_qty_to_done, 8)
        # Return the remaining quantity to the customer
        delivery_form = Form(
            self.env["prescription.delivery.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_delivery_type="return",
            )
        )
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        second_move = prescription.move_ids - first_move
        second_move.quantity_done = 8
        self.assertEqual(prescription.delivered_qty, 10)
        self.assertEqual(prescription.remaining_qty, 0)
        self.assertEqual(prescription.delivered_qty_done, 2)
        self.assertEqual(prescription.remaining_qty_to_done, 8)
        self.assertEqual(prescription.state, "waiting_return")
        # remaining_qty is 0 but prescription is not set to 'returned' until
        # remaining_qty_to_done is less than or equal to 0
        picking_2 = second_move.picking_id
        picking_2.button_validate()
        self.assertEqual(picking_2.state, "done")
        self.assertEqual(prescription.delivered_qty, 10)
        self.assertEqual(prescription.remaining_qty, 0)
        self.assertEqual(prescription.delivered_qty_done, 10)
        self.assertEqual(prescription.remaining_qty_to_done, 0)
        # The Prescription is now in 'returned' state
        self.assertEqual(prescription.state, "returned")
        self.assertFalse(prescription.can_be_refunded)
        self.assertFalse(prescription.can_be_returned)
        self.assertFalse(prescription.can_be_replaced)

    def test_finish_prescription(self):
        # Create, confirm and receive an Prescription
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        prescription.action_finish()
        finalization_form = Form(
            self.env["prescription.finalization.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_finalization_type="replace",
            )
        )
        finalization_form.finalization_id = self.finalization_reason_2
        finalization_wizard = finalization_form.save()
        finalization_wizard.action_finish()
        self.assertEqual(prescription.state, "finished")
        self.assertEqual(prescription.finalization_id, self.finalization_reason_2)

    def test_mass_return_to_customer(self):
        # Create, confirm and receive prescription_1
        prescription_1 = self._create_confirm_receive(
            self.partner, self.product, 10, self.prescription_loc
        )
        # create, confirm and receive 3 more Prescription
        # prescription_2: Same partner and same product as prescription_1
        prescription_2 = self._create_confirm_receive(
            self.partner, self.product, 15, self.prescription_loc
        )
        # prescription_3: Same partner and different product than prescription_1
        product = self.product_product.create(
            {"name": "Product 2 test", "type": "product"}
        )
        prescription_3 = self._create_confirm_receive(self.partner, product, 20, self.prescription_loc)
        # prescription_4: Different partner and same product as prescription_1
        partner = self.res_partner.create({"name": "Partner 2 test"})
        prescription_4 = self._create_confirm_receive(partner, product, 25, self.prescription_loc)
        # all prescription are ready to be returned to the customer
        all_prescription = prescription_1 | prescription_2 | prescription_3 | prescription_4
        self.assertEqual(all_prescription.mapped("state"), ["received"] * 4)
        self.assertEqual(all_prescription.mapped("can_be_returned"), [True] * 4)
        # Mass return of those four Prescription
        delivery_wizard = (
            self.env["prescription.delivery.wizard"]
            .with_context(active_ids=all_prescription.ids, prescription_delivery_type="return")
            .create({})
        )
        delivery_wizard.action_deliver()
        # Two pickings were created
        pick_1 = (prescription_1 | prescription_2 | prescription_3).mapped("move_ids.picking_id")
        pick_2 = prescription_4.move_ids.picking_id
        self.assertEqual(len(pick_1), 1)
        self.assertEqual(len(pick_2), 1)
        self.assertNotEqual(pick_1, pick_2)
        self.assertEqual((pick_1 | pick_2).mapped("state"), ["assigned"] * 2)
        # One picking per partner
        self.assertNotEqual(pick_1.partner_id, pick_2.partner_id)
        self.assertEqual(
            pick_1.partner_id,
            (prescription_1 | prescription_2 | prescription_3).mapped("partner_shipping_id"),
        )
        self.assertEqual(pick_2.partner_id, prescription_4.partner_id)
        # Each Prescription of (prescription_1, prescription_2 and prescription_3) is linked to a different
        # line of picking_1
        self.assertEqual(len(pick_1.move_ids), 3)
        self.assertEqual(
            pick_1.move_ids.mapped("prescription_id"),
            (prescription_1 | prescription_2 | prescription_3),
        )
        self.assertEqual(
            (prescription_1 | prescription_2 | prescription_3).mapped("move_ids"),
            pick_1.move_ids,
        )
        # prescription_4 is linked with the unique move of pick_2
        self.assertEqual(len(pick_2.move_ids), 1)
        self.assertEqual(pick_2.move_ids.prescription_id, prescription_4)
        self.assertEqual(prescription_4.move_ids, pick_2.move_ids)
        # Assert product and quantities are propagated correctly
        for prescription in all_prescription:
            self.assertEqual(prescription.product_id, prescription.move_ids.product_id)
            self.assertEqual(prescription.product_uom_qty, prescription.move_ids.product_uom_qty)
            self.assertEqual(prescription.product_uom, prescription.move_ids.product_uom)
            prescription.move_ids.quantity_done = prescription.product_uom_qty
        pick_1.button_validate()
        pick_2.button_validate()
        self.assertEqual(all_prescription.mapped("state"), ["returned"] * 4)

    def test_mass_return_to_customer_ungrouped(self):
        """We can choose to avoid the customer returns grouping"""
        self.env.company.prescription_return_grouping = False
        # Create, confirm and receive prescription_1
        prescription_1 = self._create_confirm_receive(
            self.partner, self.product, 10, self.prescription_loc
        )
        # create, confirm and receive 3 more Prescription
        # prescription_2: Same partner and same product as prescription_1
        prescription_2 = self._create_confirm_receive(
            self.partner, self.product, 15, self.prescription_loc
        )
        # prescription_3: Same partner and different product than prescription_1
        product = self.product_product.create(
            {"name": "Product 2 test", "type": "product"}
        )
        prescription_3 = self._create_confirm_receive(self.partner, product, 20, self.prescription_loc)
        # prescription_4: Different partner and same product as prescription_1
        partner = self.res_partner.create({"name": "Partner 2 test"})
        prescription_4 = self._create_confirm_receive(partner, product, 25, self.prescription_loc)
        # all prescription are ready to be returned to the customer
        all_prescription = prescription_1 | prescription_2 | prescription_3 | prescription_4
        self.assertEqual(all_prescription.mapped("state"), ["received"] * 4)
        self.assertEqual(all_prescription.mapped("can_be_returned"), [True] * 4)
        # Mass return of those four Prescription
        delivery_wizard = (
            self.env["prescription.delivery.wizard"]
            .with_context(active_ids=all_prescription.ids, prescription_delivery_type="return")
            .create({})
        )
        delivery_wizard.action_deliver()
        self.assertEqual(4, len(all_prescription.move_ids.picking_id))

    def test_prescription_from_picking_return(self):
        # Create a return from a delivery picking
        origin_delivery = self._create_delivery()
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=origin_delivery.ids,
                active_id=origin_delivery.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_prescription = True
        return_wizard = stock_return_picking_form.save()
        picking_action = return_wizard.create_returns()
        # Each origin move is linked to a different Prescription
        origin_moves = origin_delivery.move_ids
        self.assertTrue(origin_moves[0].prescription_ids)
        self.assertTrue(origin_moves[1].prescription_ids)
        prescription = origin_moves.mapped("prescription_ids")
        self.assertEqual(prescription.mapped("state"), ["confirmed"] * 2)
        # Each reception move is linked one of the generated Prescription
        reception = self.env["stock.picking"].browse(picking_action["res_id"])
        reception_moves = reception.move_ids
        self.assertTrue(reception_moves[0].prescription_receiver_ids)
        self.assertTrue(reception_moves[1].prescription_receiver_ids)
        self.assertEqual(reception_moves.mapped("prescription_receiver_ids"), prescription)
        # Validate the reception picking to set prescription to 'received' state
        reception_moves[0].quantity_done = reception_moves[0].product_uom_qty
        reception_moves[1].quantity_done = reception_moves[1].product_uom_qty
        reception.button_validate()
        self.assertEqual(prescription.mapped("state"), ["received"] * 2)

    def test_split(self):
        origin_delivery = self._create_delivery()
        prescription_form = Form(self.env["prescription"])
        prescription_form.partner_id = self.partner
        prescription_form.picking_id = origin_delivery
        prescription_form.move_id = origin_delivery.move_ids.filtered(
            lambda r: r.product_id == self.product
        )
        prescription = prescription_form.save()
        prescription.action_confirm()
        prescription.reception_move_id.quantity_done = 10
        prescription.reception_move_id.picking_id._action_done()
        # Return quantity 4 of the same product to the customer
        delivery_form = Form(
            self.env["prescription.delivery.wizard"].with_context(
                active_ids=prescription.ids,
                prescription_delivery_type="return",
            )
        )
        delivery_form.product_uom_qty = 4
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        prescription.move_ids.quantity_done = 4
        prescription.move_ids.picking_id.button_validate()
        self.assertEqual(prescription.state, "waiting_return")
        # Extract the remaining quantity to another Prescription
        self.assertTrue(prescription.can_be_split)
        split_wizard = (
            self.env["prescription.split.wizard"]
            .with_context(
                active_id=prescription.id,
                active_ids=prescription.ids,
            )
            .create({})
        )
        action = split_wizard.action_split()
        # Check prescription is set to 'returned' after split. Check new_prescription values
        self.assertEqual(prescription.state, "returned")
        new_prescription = self.env["prescription"].browse(action["res_id"])
        self.assertEqual(new_prescription.origin_split_prescription_id, prescription)
        self.assertEqual(new_prescription.delivered_qty, 0)
        self.assertEqual(new_prescription.remaining_qty, 6)
        self.assertEqual(new_prescription.delivered_qty_done, 0)
        self.assertEqual(new_prescription.remaining_qty_to_done, 6)
        self.assertEqual(new_prescription.state, "received")
        self.assertTrue(new_prescription.can_be_refunded)
        self.assertTrue(new_prescription.can_be_returned)
        self.assertTrue(new_prescription.can_be_replaced)
        self.assertEqual(new_prescription.move_id, prescription.move_id)
        self.assertEqual(new_prescription.reception_move_id, prescription.reception_move_id)
        self.assertEqual(new_prescription.product_uom_qty + prescription.product_uom_qty, 10)
        self.assertEqual(new_prescription.move_id.quantity_done, 10)
        self.assertEqual(new_prescription.reception_move_id.quantity_done, 10)

    def test_prescription_to_receive_on_delete_invoice(self):
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        prescription.action_refund()
        self.assertEqual(prescription.state, "refunded")
        prescription.refund_id.unlink()
        self.assertFalse(prescription.refund_id)
        self.assertEqual(prescription.state, "received")
        self.assertTrue(prescription.can_be_refunded)
        self.assertTrue(prescription.can_be_returned)
        self.assertTrue(prescription.can_be_replaced)

    def test_prescription_picking_type_default_values(self):
        warehouse = self.env["stock.warehouse"].create(
            {"name": "Stock - Prescription Test", "code": "SRT"}
        )
        self.assertFalse(warehouse.prescription_in_type_id.use_create_lots)
        self.assertTrue(warehouse.prescription_in_type_id.use_existing_lots)

    def test_quantities_on_hand(self):
        prescription = self._create_confirm_receive(self.partner, self.product, 10, self.prescription_loc)
        self.assertEqual(prescription.product_id.qty_available, 0)

    def test_autoconfirm_email(self):
        self.company.send_prescription_confirmation = True
        self.company.send_prescription_receipt_confirmation = True
        self.company.send_prescription_draft_confirmation = True
        self.company.prescription_mail_confirmation_template_id = self.env.ref(
            "prescription.mail_template_prescription_notification"
        )
        self.company.prescription_mail_receipt_confirmation_template_id = self.env.ref(
            "prescription.mail_template_prescription_receipt_notification"
        )
        self.company.prescription_mail_draft_confirmation_template_id = self.env.ref(
            "prescription.mail_template_prescription_draft_notification"
        )
        previous_mails = self.env["mail.mail"].search(
            [("partner_ids", "in", self.partner.ids)]
        )
        self.assertFalse(previous_mails)
        # Force the context to mock an Prescription created from the portal, which is
        # feature that we get on `prescription_sale`. We drop it after the Prescription creation
        # to avoid uncontrolled side effects
        ctx = self.env.context
        self.env.context = dict(ctx, from_portal=True)
        prescription = self._create_prescription(self.partner, self.product, 10, self.prescription_loc)
        self.env.context = ctx
        mail_draft = self.env["mail.message"].search(
            [("partner_ids", "in", self.partner.ids)]
        )
        prescription.action_confirm()
        mail_confirm = (
            self.env["mail.message"].search([("partner_ids", "in", self.partner.ids)])
            - mail_draft
        )
        self.assertTrue(prescription.name in mail_confirm.subject)
        self.assertTrue(prescription.name in mail_confirm.body)
        self.assertEqual(
            self.env.ref("prescription.mt_prescription_notification"), mail_confirm.subtype_id
        )
        # Now we'll confirm the incoming goods picking and the automatic
        # reception notification should be sent
        prescription.reception_move_id.quantity_done = prescription.product_uom_qty
        prescription.reception_move_id.picking_id.button_validate()
        mail_receipt = (
            self.env["mail.message"].search([("partner_ids", "in", self.partner.ids)])
            - mail_draft
            - mail_confirm
        )
        self.assertTrue(prescription.name in mail_receipt.subject)
        self.assertTrue("products received" in mail_receipt.subject)
