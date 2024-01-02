# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.tests import tagged, common, Form
from odoo.tools import float_compare, float_is_zero


@tagged('post_install', '-at_install')
class TestPrescription(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partners
        cls.res_partner_1 = cls.env['res.partner'].create({'name': 'Wood Corner'})
        cls.res_partner_address_1 = cls.env['res.partner'].create({'name': 'Willie Burke', 'parent_id': cls.res_partner_1.id})
        cls.res_partner_12 = cls.env['res.partner'].create({'name': 'Partner 12'})

        # Products
        cls.product_product_3 = cls.env['product.product'].create({'name': 'Desk Combination'})
        cls.product_product_11 = cls.env['product.product'].create({
            'name': 'Conference Chair',
            'lst_price': 30.0,
            })
        cls.product_product_5 = cls.env['product.product'].create({'name': 'Product 5'})
        cls.product_product_6 = cls.env['product.product'].create({'name': 'Large Cabinet'})
        cls.product_product_12 = cls.env['product.product'].create({'name': 'Office Chair Black'})
        cls.product_product_13 = cls.env['product.product'].create({'name': 'Corner Desk Left Sit'})

        # Storable products
        cls.product_storable_no = cls.env['product.product'].create({
            'name': 'Product Storable No Tracking',
            'type': 'product',
            'tracking': 'none',
        })
        cls.product_storable_serial = cls.env['product.product'].create({
            'name': 'Product Storable Serial',
            'type': 'product',
            'tracking': 'serial',
        })
        cls.product_storable_lot = cls.env['product.product'].create({
            'name': 'Product Storable Lot',
            'type': 'product',
            'tracking': 'lot',
        })

        # 'Create Prescription' Products
        cls.product_consu_order_prescription = cls.env['product.product'].create({
            'name': 'Prescription Consumable',
            'type': 'consu',
            'create_prescription': True,
        })
        cls.product_storable_order_prescription = cls.env['product.product'].create({
            'name': 'Prescription Storable',
            'type': 'product',
            'create_prescription': True,
        })
        cls.product_service_order_prescription = cls.env['product.product'].create({
            'name': 'Prescription Service',
            'type': 'service',
            'create_prescription': True,
        })

        # Location
        cls.stock_warehouse = cls.env['stock.warehouse'].search([('company_id', '=', cls.env.company.id)], limit=1)
        cls.stock_location_14 = cls.env['stock.location'].create({
            'name': 'Shelf 2',
            'location_id': cls.stock_warehouse.lot_stock_id.id,
        })

        # Prescription Orders
        cls.prescription1 = cls.env['prescription.order'].create({
            'product_id': cls.product_product_3.id,
            'product_uom': cls.env.ref('uom.product_uom_unit').id,
            'picking_type_id': cls.stock_warehouse.prescription_type_id.id,
            'move_ids': [
                (0, 0, {
                    'product_id': cls.product_product_11.id,
                    'product_uom_qty': 1.0,
                    'state': 'draft',
                    'prescription_line_type': 'add',
                    'company_id': cls.env.company.id,
                })
            ],
            'partner_id': cls.res_partner_12.id,
        })

        cls.prescription0 = cls.env['prescription.order'].create({
            'product_id': cls.product_product_5.id,
            'product_uom': cls.env.ref('uom.product_uom_unit').id,
            'user_id': False,
            'picking_type_id': cls.stock_warehouse.prescription_type_id.id,
            'move_ids': [
                (0, 0, {
                    'product_id': cls.product_product_12.id,
                    'product_uom_qty': 1.0,
                    'state': 'draft',
                    'prescription_line_type': 'add',
                    'company_id': cls.env.company.id,
                })
            ],
            'partner_id': cls.res_partner_12.id,
        })

        cls.prescription2 = cls.env['prescription.order'].create({
            'product_id': cls.product_product_6.id,
            'product_uom': cls.env.ref('uom.product_uom_unit').id,
            'user_id': False,
            'picking_type_id': cls.stock_warehouse.prescription_type_id.id,
            'move_ids': [
                (0, 0, {
                    'product_id': cls.product_product_13.id,
                    'product_uom_qty': 1.0,
                    'state': 'draft',
                    'prescription_line_type': 'add',
                    'company_id': cls.env.company.id,
                })
            ],
            'partner_id': cls.res_partner_12.id,
        })

        cls.env.user.groups_id |= cls.env.ref('stock.group_stock_user')

    def _create_simple_prescription_order(self):
        product_to_prescription = self.product_product_5
        return self.env['prescription.order'].create({
            'product_id': product_to_prescription.id,
            'product_uom': product_to_prescription.uom_id.id,
            'picking_type_id': self.stock_warehouse.prescription_type_id.id,
            'partner_id': self.res_partner_12.id
        })

    def _create_simple_part_move(self, prescription_id=False, qty=0.0, product=False):
        if not product:
            product = self.product_product_5
        return self.env['stock.move'].create({
            'prescription_line_type': 'add',
            'product_id': product.id,
            'product_uom_qty': qty,
            'prescription_id': prescription_id,
            'company_id': self.env.company.id,
        })

    @classmethod
    def create_quant(cls, product, qty, offset=0, name="L"):
        i = 1
        if product.tracking == 'serial':
            i, qty = qty, 1
            if name == "L":
                name = "S"

        vals = []
        for x in range(1, i + 1):
            qDict = {
                'location_id': cls.stock_warehouse.lot_stock_id.id,
                'product_id': product.id,
                'inventory_quantity': qty,
            }

            if product.tracking != 'none':
                qDict['lot_id'] = cls.env['stock.lot'].create({
                    'name': name + str(offset + x),
                    'product_id': product.id,
                    'company_id': cls.env.company.id
                }).id
            vals.append(qDict)

        return cls.env['stock.quant'].create(vals)

    def test_01_prescription_states_transition(self):
        prescription = self._create_simple_prescription_order()
        # Draft -> Confirmed -> Cancel -> Draft -> Done -> Failing Cancel
        # draft -> confirmed (action_validate -> _action_prescription_confirm)
            # PRE
                # lines' qty >= 0 !-> UserError
                # product's qty IS available !-> Warning w/ choice
            # POST
                # state = confirmed
                # move_ids in (partially reserved, fully reserved, waiting availability)

        #  Line A with qty < 0 --> UserError
        lineA = self._create_simple_part_move(prescription.id, -1.0, self.product_storable_no)
        prescription.move_ids |= lineA
        with self.assertRaises(UserError):
            prescription.action_validate()

        #  Line A with qty > 0 & not available, Line B with qty >= 0 & available --> Warning (stock.warn.insufficient.qty.prescription)
        lineA.product_uom_qty = 2.0
        lineB = self._create_simple_part_move(prescription.id, 2.0, self.product_storable_lot)
        prescription.move_ids |= lineB
        quant = self.create_quant(self.product_storable_no, 1)
        quant |= self.create_quant(self.product_storable_lot, 3)
        quant.action_apply_inventory()

        lineC = self._create_simple_part_move(prescription.id, 1.0, self.product_storable_order_prescription)
        prescription.move_ids |= lineC

        prescription.product_id = self.product_storable_serial
        validate_action = prescription.action_validate()
        self.assertEqual(validate_action.get("res_model"), "stock.warn.insufficient.qty.prescription")
        # Warn qty Wizard only apply to "product TO prescription"
        warn_qty_wizard = Form(
            self.env['stock.warn.insufficient.qty.prescription']
            .with_context(**validate_action['context'])
            ).save()
        warn_qty_wizard.action_done()

        self.assertEqual(prescription.state, "confirmed", 'Prescription order should be in "Confirmed" state.')
        self.assertEqual(lineA.state, "partially_available", 'Prescription line #1 should be in "Partial Availability" state.')
        self.assertEqual(lineB.state, "assigned", 'Prescription line #2 should be in "Available" state.')
        self.assertEqual(lineC.state, "confirmed", 'Prescription line #3 should be in "Waiting Availability" state.')

        # Create quotation
        # No partner warning -> working case -> already linked warning

        # Ensure SO doesn't exist
        self.assertEqual(len(prescription.sale_order_id), 0)
        prescription.partner_id = None
        with self.assertRaises(UserError) as err:
            prescription.action_create_sale_order()
        self.assertIn("You need to define a customer", err.exception.args[0])
        prescription.partner_id = self.res_partner_12.id
        prescription.action_create_sale_order()
        # Ensure SO and SOL were created
        self.assertNotEqual(len(prescription.sale_order_id), 0)
        self.assertEqual(len(prescription.sale_order_id.order_line), 3)
        with self.assertRaises(UserError) as err:
            prescription.action_create_sale_order()

        # (*) -> cancel (action_prescription_cancel)
            # PRE
                # state != done !-> UserError (cf. end of this test)
            # POST
                # moves_ids state == cancelled
                # 'Lines" SOL product_uom_qty == 0
                # state == cancel

        self.assertNotEqual(prescription.state, "done")
        prescription.action_prescription_cancel()
        self.assertEqual(prescription.state, "cancel")
        self.assertTrue(all(m.state == "cancel" for m in prescription.move_ids))
        self.assertTrue(all(float_is_zero(sol.product_uom_qty, 2) for sol in prescription.sale_order_id.order_line))

        # (*)/cancel -> draft (action_prescription_cancel_draft)
            # PRE
                # state == cancel !-> action_prescription_cancel()
                # state != done !~> UserError (transitive..., don't care)
            # POST
                # move_ids.state == draft
                # state == draft

        prescription.action_prescription_cancel_draft()
        self.assertEqual(prescription.state, "draft")
        self.assertTrue(all(m.state == "draft" for m in prescription.move_ids))

        # draft -> confirmed
            # Enforce product_id availability to skip warning
        quant = self.create_quant(self.product_storable_serial, 1)
        quant.action_apply_inventory()
        prescription.lot_id = quant.lot_id
        prescription.action_validate()
        self.assertEqual(prescription.state, "confirmed")

        # confirmed -> in_progress (action_prescription_start)
            # Purely informative state
        prescription.action_prescription_start()
        self.assertEqual(prescription.state, "in_progress")

        # in_progress -> done (action_prescription_end -> action_prescription_done)
            # PRE
                # state == in_progress !-> UserError
                # lines' quantity >= lines' product_uom_qty !-> Warning
                # line tracked => line has lot_ids !-> ValidationError
            # POST
                # lines with quantity == 0 are cancelled (related sol product_uom_qty is consequently set to 0)
                # prescription.product_id => prescription.move_id
                # move_ids.state == (done || cancel)
                # state == done
                # move_ids with quantity (LOWER or HIGHER than) product_uom_qty MUST NOT be splitted
        # Any line with quantity < product_uom_qty => Warning
        prescription.move_ids.picked = True
        end_action = prescription.action_prescription_end()
        self.assertEqual(end_action.get("res_model"), "prescription.warn.uncomplete.move")
        warn_uncomplete_wizard = Form(
            self.env['prescription.warn.uncomplete.move']
            .with_context(**end_action['context'])
            ).save()
        # LineB : no serial => ValidationError
        lot = lineB.move_line_ids.lot_id
        with self.assertRaises(UserError) as err:
            lineB.move_line_ids.lot_id = False
            warn_uncomplete_wizard.action_validate()

        # LineB with lots
        lineB.move_line_ids.lot_id = lot

        lineA.quantity = 2  # quantity = product_uom_qty
        lineC.quantity = 2  # quantity > product_uom_qty (No warning)
        lineD = self._create_simple_part_move(prescription.id, 0.0)
        prescription.move_ids |= lineD  # product_uom_qty = 0   : state is cancelled

        self.assertEqual(lineD.state, 'assigned')
        num_of_lines = len(prescription.move_ids)
        self.assertFalse(prescription.move_id)
        prescription.action_prescription_end()

        self.assertEqual(prescription.state, "done")
        done_moves = prescription.move_ids - lineD
        #line a,b,c are 'done', line d is 'cancel'
        self.assertTrue(all(m.state == 'done' for m in done_moves))
        self.assertEqual(lineD.state, 'cancel')
        self.assertEqual(len(prescription.move_id), 1)
        self.assertEqual(len(prescription.move_ids), num_of_lines)  # No split

        # (*) -> cancel (action_prescription_cancel)
            # PRE
                # state != done !-> UserError
        with self.assertRaises(UserError) as err:
            prescription.action_prescription_cancel()

    def test_02_prescription_sale_order_binding(self):
        # Binding from SO to RX(s)
        #   On SO Confirm
        #     - Create linked RX per line (only if item with "create_prescription" checked)
        #   Create Prescription SOL
        #     - sol qty updated to 0 -> RX canceled (Reciprocal is true too)
        #     - sol qty back to >0 -> RX Confirmed (Reciprocal is not true)
        #   RX Parts SOL
        #     - SOL qty change is NOT propagated to RX
        #     - However, these changes FROM RX are propagated to SO
        #----------------------------------------------------------------------------------
        #  Binding from RX to SO
        so_form = Form(self.env['sale.order'])
        so_form.partner_id = self.res_partner_1
        with so_form.order_line.new() as line:
            line.product_id = self.product_consu_order_prescription
            line.product_uom_qty = 2.0
        sale_order = so_form.save()
        order_line = sale_order.order_line[0]
        self.assertEqual(len(sale_order.prescription_order_ids), 0)
        sale_order.action_confirm()
        # Quantity set on the "create prescription" product doesn't affect the number of RX created
        self.assertEqual(len(sale_order.prescription_order_ids), 1)
        prescription_order = sale_order.prescription_order_ids[0]
        self.assertEqual(sale_order, prescription_order.sale_order_id)
        self.assertEqual(prescription_order.state, 'confirmed')
        order_line.product_uom_qty = 0
        self.assertEqual(prescription_order.state, 'cancel')
        order_line.product_uom_qty = 1
        self.assertEqual(prescription_order.state, 'confirmed')
        prescription_order.action_prescription_cancel()
        self.assertTrue(float_is_zero(order_line.product_uom_qty, 2))
        order_line.product_uom_qty = 3
        self.assertEqual(prescription_order.state, 'confirmed')
        # Add RX line
        rx_form = Form(prescription_order)
        with rx_form.move_ids.new() as rx_line_form:
            rx_line_form.prescription_line_type = 'add'
            rx_line_form.product_id = self.product_product_11
            rx_line_form.product_uom_qty = 1
        rx_form.save()
        rx_line_0 = prescription_order.move_ids[0]
        sol_part_0 = rx_line_0.sale_line_id
        self.assertEqual(float_compare(sol_part_0.product_uom_qty, rx_line_0.product_uom_qty, 2), 0)
        # chg qty in SO -> No effect on RX
        sol_part_0.product_uom_qty = 5
        self.assertNotEqual(float_compare(sol_part_0.product_uom_qty, rx_line_0.product_uom_qty, 2), 0)
        # chg qty in RX -> Update qty in SO
        rx_line_0.product_uom_qty = 3
        self.assertEqual(float_compare(sol_part_0.product_uom_qty, rx_line_0.product_uom_qty, 2), 0)
        # with/without warranty
        self.assertFalse(float_is_zero(sol_part_0.price_unit, 2))
        prescription_order.under_warranty = True
        self.assertTrue(float_is_zero(sol_part_0.price_unit, 2))
        prescription_order.under_warranty = False
        self.assertFalse(float_is_zero(sol_part_0.price_unit, 2))

        # stock_move transitions
        #   add -> remove -> add -> recycle -> add transitions
        rx_line_0.prescription_line_type = 'remove'
        self.assertTrue(float_is_zero(sol_part_0.product_uom_qty, 2))
        rx_line_0.prescription_line_type = 'add'
        self.assertEqual(float_compare(sol_part_0.product_uom_qty, rx_line_0.product_uom_qty, 2), 0)
        rx_line_0.prescription_line_type = 'recycle'
        self.assertTrue(float_is_zero(sol_part_0.product_uom_qty, 2))
        rx_line_0.prescription_line_type = 'add'
        self.assertEqual(float_compare(sol_part_0.product_uom_qty, rx_line_0.product_uom_qty, 2), 0)
        #   remove and recycle line : not added to SO.
        sol_count = len(sale_order.order_line)
        with rx_form.move_ids.new() as rx_line_form:
            rx_line_form.prescription_line_type = 'remove'
            rx_line_form.product_id = self.product_product_12
            rx_line_form.product_uom_qty = 1
        with rx_form.move_ids.new() as rx_line_form:
            rx_line_form.prescription_line_type = 'recycle'
            rx_line_form.product_id = self.product_product_13
            rx_line_form.product_uom_qty = 1
        rx_form.save()
        rx_line_1 = prescription_order.move_ids[1]
        self.assertEqual(len(sale_order.order_line), sol_count)
        # remove to add -> added to SO
        rx_line_1.prescription_line_type = 'add'
        sol_part_1 = rx_line_1.sale_line_id
        self.assertNotEqual(len(sale_order.order_line), sol_count)
        self.assertEqual(float_compare(sol_part_1.product_uom_qty, rx_line_1.product_uom_qty, 2), 0)
        # delete 'remove to add' line in RX -> SOL qty set to 0
        prescription_order.move_ids = [(2, rx_line_1.id, 0)]
        self.assertTrue(float_is_zero(sol_part_1.product_uom_qty, 2))

        # prescription_order.action_prescription_end()
        #   -> order_line.qty_delivered == order_line.product_uom_qty
        #   -> "RX Lines"'s SOL.qty_delivered == move.quantity
        prescription_order.action_prescription_start()
        for line in prescription_order.move_ids:
            line.quantity = line.product_uom_qty
        prescription_order.action_prescription_end()
        self.assertTrue(float_is_zero(order_line.qty_delivered, 2))
        self.assertEqual(float_compare(sol_part_0.product_uom_qty, rx_line_0.quantity, 2), 0)
        self.assertTrue(float_is_zero(sol_part_1.qty_delivered, 2))

    def test_03_sale_order_delivered_qty(self):
        so_form = Form(self.env['sale.order'])
        so_form.partner_id = self.res_partner_1
        with so_form.order_line.new() as line:
            line.product_id = self.product_consu_order_prescription
            line.product_uom_qty = 1.0
        with so_form.order_line.new() as line:
            line.product_id = self.product_storable_order_prescription
            line.product_uom_qty = 1.0
        with so_form.order_line.new() as line:
            line.product_id = self.product_service_order_prescription
            line.product_uom_qty = 1.0
        sale_order = so_form.save()
        sale_order.action_confirm()

        prescription_order_ids = sale_order.prescription_order_ids
        prescription_order_ids.action_prescription_start()
        prescription_order_ids.action_prescription_end()

        for sol in sale_order.order_line:
            if sol.product_template_id.type == 'service':
                self.assertEqual(float_compare(sol.product_uom_qty, sol.qty_delivered, 2), 0)
            else:
                self.assertTrue(float_is_zero(sol.qty_delivered, 2))

    def test_prescription_return(self):
        """Tests functionality of creating a prescription directly from a return picking,
        i.e. prescription can be made and defaults to appropriate return values. """
        # test return
        # Required for `location_dest_id` to be visible in the view
        self.env.user.groups_id += self.env.ref('stock.group_stock_multi_locations')
        picking_form = Form(self.env['stock.picking'])
        picking_form.picking_type_id = self.stock_warehouse.in_type_id
        picking_form.partner_id = self.res_partner_1
        picking_form.location_dest_id = self.stock_location_14
        return_picking = picking_form.save()

        # create prescription
        res_dict = return_picking.action_prescription_return()
        prescription_form = Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context']))
        prescription_form.product_id = self.product_product_3
        prescription = prescription_form.save()

        # test that the resulting prescriptions are correctly created
        self.assertEqual(len(return_picking.prescription_ids), 1, "A prescription order should have been created and linked to original return.")
        for prescription in return_picking.prescription_ids:
            self.assertEqual(prescription.location_id, return_picking.location_dest_id, "Prescription location should have defaulted to return destination location")
            self.assertEqual(prescription.partner_id, return_picking.partner_id, "Prescription customer should have defaulted to return customer")
            self.assertEqual(prescription.picking_type_id, return_picking.picking_type_id.warehouse_id.prescription_type_id)

    def test_prescription_compute_product_uom(self):
        prescription = self.env['prescription.order'].create({
            'product_id': self.product_product_3.id,
            'picking_type_id': self.stock_warehouse.prescription_type_id.id,
            'move_ids': [
                (0, 0, {
                    'prescription_line_type': 'add',
                    'product_id': self.product_product_11.id,
                })
            ],
        })
        self.assertEqual(prescription.product_uom, self.product_product_3.uom_id)
        self.assertEqual(prescription.move_ids[0].product_uom, self.product_product_11.uom_id)

    def test_prescription_compute_location(self):
        prescription = self.env['prescription.order'].create({
            'product_id': self.product_product_3.id,
            'picking_type_id': self.stock_warehouse.prescription_type_id.id,
            'move_ids': [
                (0, 0, {
                    'prescription_line_type': 'add',
                    'product_id': self.product_product_11.id,
                })
            ],
        })
        self.assertEqual(prescription.location_id, self.stock_warehouse.lot_stock_id)
        self.assertEqual(prescription.move_ids[0].location_id, self.stock_warehouse.lot_stock_id)
        location_dest_id = self.env['stock.location'].search([
            ('usage', '=', 'production'),
            ('company_id', '=', prescription.company_id.id),
        ], limit=1)
        self.assertEqual(prescription.move_ids[0].location_dest_id, location_dest_id)

    def test_purchase_price_so_create_from_prescription(self):
        """
        Test that the purchase price is correctly set on the SO line,
        when creating a SO from a prescription order.
        """
        if not self.env['ir.module.module'].search([('name', '=', 'sale_margin'), ('state', '=', 'installed')]):
            self.skipTest("sale_margin is not installed, so there is no purchase price to test")
        self.product_product_11.standard_price = 10
        prescription = self.env['prescription.order'].create({
            'partner_id': self.res_partner_1.id,
            'product_id': self.product_product_3.id,
            'picking_type_id': self.stock_warehouse.prescription_type_id.id,
            'move_ids': [
                (0, 0, {
                    'prescription_line_type': 'add',
                    'product_id': self.product_product_11.id,
                })
            ],
        })
        prescription.action_create_sale_order()
        self.assertEqual(prescription.sale_order_id.order_line.product_id, self.product_product_11)
        self.assertEqual(prescription.sale_order_id.order_line.purchase_price, 10)

    def test_prescription_from_return(self):
        """
        create a prescription order from a return delivery and ensure that the stock.move
        resulting from the prescription is not associated with the return picking.
        """

        product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
        })
        self.env['stock.quant']._update_available_quantity(product, self.stock_location_14, 1)
        picking_form = Form(self.env['stock.picking'])
        #create a delivery order
        picking_form.picking_type_id = self.stock_warehouse.out_type_id
        picking_form.partner_id = self.res_partner_1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = 1.0
        picking = picking_form.save()
        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()

        self.assertEqual(picking.state, 'done')
        # Create a return
        stock_return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.ids[0],
            active_model='stock.picking'))
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = 1.0
        stock_return_picking_action = stock_return_picking.create_returns()
        return_picking = self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_picking.move_ids.picked = True
        return_picking.button_validate()
        self.assertEqual(return_picking.state, 'done')

        res_dict = return_picking.action_prescription_return()
        prescription_form = Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context']))
        prescription_form.product_id = product
        prescription = prescription_form.save()
        prescription.action_prescription_start()
        prescription.action_prescription_end()
        self.assertEqual(prescription.state, 'done')
        self.assertEqual(len(return_picking.move_ids), 1)
