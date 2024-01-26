# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import ValuationReconciliationTestCommon
from odoo.addons.pod_prescriptions.tests.common import TestPrescriptionCommon
from odoo.exceptions import UserError
from odoo.tests import Form, tagged


@tagged('post_install', '-at_install')
class TestPrescriptionStock(TestPrescriptionCommon, ValuationReconciliationTestCommon):

    def _get_new_prescriptions_order(self, amount=10.0, product=False):
        """ Creates and returns a prescriptions order with one default order line.

        :param float amount: quantity of product for the order line (10 by default)
        """
        product = product or self.company_data['product_delivery_no']
        prescriptions_order_vals = {
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': amount,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price})],
            'pricelist_id': self.company_data['default_pricelist'].id,
        }
        prescriptions_order = self.env['prescriptions.order'].create(prescriptions_order_vals)
        return prescriptions_order

    def test_00_prescriptions_stock_invoice(self):
        """
        Test RX's changes when playing around with stock moves, quants, pack operations, pickings
        and whatever other model there is in stock with "invoice on delivery" products
        """
        self.rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': p.name,
                    'product_id': p.id,
                    'product_uom_qty': 2,
                    'product_uom': p.uom_id.id,
                    'price_unit': p.list_price,
                }) for p in (
                    self.company_data['product_order_no'],
                    self.company_data['product_service_delivery'],
                    self.company_data['product_service_order'],
                    self.company_data['product_delivery_no'],
                )],
            'pricelist_id': self.company_data['default_pricelist'].id,
            'picking_policy': 'direct',
        })

        # confirm our standard rx, check the picking
        self.rx.action_confirm()
        self.assertTrue(self.rx.picking_ids, 'Prescription Stock: no picking created for "invoice on delivery" storable products')
        # invoice on order
        self.rx._create_invoices()

        # deliver partially, check the rx's invoice_status and delivered quantities
        self.assertEqual(self.rx.invoice_status, 'no', 'Prescription Stock: rx invoice_status should be "nothing to invoice" after invoicing')
        pick = self.rx.picking_ids
        pick.move_ids.write({'quantity': 1, 'picked': True})
        wiz_act = pick.button_validate()
        wiz = Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()
        self.assertEqual(self.rx.invoice_status, 'to invoice', 'Prescription Stock: rx invoice_status should be "to invoice" after partial delivery')
        del_qties = [rxl.qty_delivered for rxl in self.rx.order_line]
        del_qties_truth = [1.0 if rxl.product_id.type in ['product', 'consu'] else 0.0 for rxl in self.rx.order_line]
        self.assertEqual(del_qties, del_qties_truth, 'Prescription Stock: delivered quantities are wrong after partial delivery')
        # invoice on delivery: only storable products
        inv_1 = self.rx._create_invoices()
        self.assertTrue(all([il.product_id.invoice_policy == 'delivery' for il in inv_1.invoice_line_ids]),
                        'Prescription Stock: invoice should only contain "invoice on delivery" products')

        # complete the delivery and check invoice_status again
        self.assertEqual(self.rx.invoice_status, 'no',
                         'Prescription Stock: rx invoice_status should be "nothing to invoice" after partial delivery and invoicing')
        self.assertEqual(len(self.rx.picking_ids), 2, 'Prescription Stock: number of pickings should be 2')
        pick_2 = self.rx.picking_ids.filtered('backorder_id')
        pick_2.move_ids.write({'quantity': 1, 'picked': True})
        self.assertTrue(pick_2.button_validate(), 'Prescription Stock: second picking should be final without need for a backorder')
        self.assertEqual(self.rx.invoice_status, 'to invoice', 'Prescription Stock: rx invoice_status should be "to invoice" after complete delivery')
        del_qties = [rxl.qty_delivered for rxl in self.rx.order_line]
        del_qties_truth = [2.0 if rxl.product_id.type in ['product', 'consu'] else 0.0 for rxl in self.rx.order_line]
        self.assertEqual(del_qties, del_qties_truth, 'Prescription Stock: delivered quantities are wrong after complete delivery')
        # Without timesheet, we manually set the delivered qty for the product serv_del
        self.rx.order_line.sorted()[1]['qty_delivered'] = 2.0

        # There is a bug with `new` and `_origin`
        # If you create a first new from a record, then change a value on the origin record, than create another new,
        # this other new wont have the updated value of the origin record, but the one from the previous new
        # Here the problem lies in the use of `new` in `move = self_ctx.new(new_vals)`,
        # and the fact this method is called multiple times in the same transaction test case.
        # Here, we update `qty_delivered` on the origin record, but the `new` records which are in cache with this order line
        # as origin are not updated, nor the fields that depends on it.
        self.env.flush_all()
        self.env.invalidate_all()

        inv_id = self.rx._create_invoices()
        self.assertEqual(self.rx.invoice_status, 'invoiced',
                         'Prescription Stock: rx invoice_status should be "fully invoiced" after complete delivery and invoicing')

    def test_01_prescriptions_stock_order(self):
        """
        Test RX's changes when playing around with stock moves, quants, pack operations, pickings
        and whatever other model there is in stock with "invoice on order" products
        """
        # let's cheat and put all our products to "invoice on order"
        self.rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'name': p.name,
                'product_id': p.id,
                'product_uom_qty': 2,
                'product_uom': p.uom_id.id,
                'price_unit': p.list_price,
                }) for p in (
                    self.company_data['product_order_no'],
                    self.company_data['product_service_delivery'],
                    self.company_data['product_service_order'],
                    self.company_data['product_delivery_no'],
                )],
            'pricelist_id': self.company_data['default_pricelist'].id,
            'picking_policy': 'direct',
        })
        for rxl in self.rx.order_line:
            rxl.product_id.invoice_policy = 'order'
        # confirm our standard rx, check the picking
        self.rx.order_line._compute_product_updatable()
        self.assertTrue(self.rx.order_line.sorted()[0].product_updatable)
        self.rx.action_confirm()
        self.rx.order_line._compute_product_updatable()
        self.assertFalse(self.rx.order_line.sorted()[0].product_updatable)
        self.assertTrue(self.rx.picking_ids, 'Prescription Stock: no picking created for "invoice on order" storable products')
        # let's do an invoice for a deposit of 5%

        advance_product = self.env['product.product'].create({
            'name': 'Deposit',
            'type': 'service',
            'invoice_policy': 'order',
        })
        adv_wiz = self.env['prescriptions.advance.payment.inv'].with_context(active_ids=[self.rx.id]).create({
            'advance_payment_method': 'percentage',
            'amount': 5.0,
            'product_id': advance_product.id,
        })
        act = adv_wiz.with_context(open_invoices=True).create_invoices()
        inv = self.env['account.move'].browse(act['res_id'])
        self.assertEqual(inv.amount_untaxed, self.rx.amount_untaxed * 5.0 / 100.0, 'Prescription Stock: deposit invoice is wrong')
        self.assertEqual(self.rx.invoice_status, 'to invoice', 'Prescription Stock: rx should be to invoice after invoicing deposit')
        # invoice on order: everything should be invoiced
        self.rx._create_invoices(final=True)
        self.assertEqual(self.rx.invoice_status, 'invoiced', 'Prescription Stock: rx should be fully invoiced after second invoice')

        # deliver, check the delivered quantities
        pick = self.rx.picking_ids
        pick.move_ids.write({'quantity': 2, 'picked': True})
        self.assertTrue(pick.button_validate(), 'Prescription Stock: complete delivery should not need a backorder')
        del_qties = [rxl.qty_delivered for rxl in self.rx.order_line]
        del_qties_truth = [2.0 if rxl.product_id.type in ['product', 'consu'] else 0.0 for rxl in self.rx.order_line]
        self.assertEqual(del_qties, del_qties_truth, 'Prescription Stock: delivered quantities are wrong after partial delivery')
        # invoice on delivery: nothing to invoice
        with self.assertRaises(UserError):
            self.rx._create_invoices()

    def test_02_prescriptions_stock_return(self):
        """
        Test a RX with a product invoiced on delivery. Deliver and invoice the RX, then do a return
        of the picking. Check that a refund invoice is well generated.
        """
        # intial rx
        self.product = self.company_data['product_delivery_no']
        rx_vals = {
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price})],
            'pricelist_id': self.company_data['default_pricelist'].id,
        }
        self.rx = self.env['prescriptions.order'].create(rx_vals)

        # confirm our standard rx, check the picking
        self.rx.action_confirm()
        self.assertTrue(self.rx.picking_ids, 'Prescription Stock: no picking created for "invoice on delivery" storable products')

        # invoice in on delivery, nothing should be invoiced
        self.assertEqual(self.rx.invoice_status, 'no', 'Prescription Stock: rx invoice_status should be "no" instead of "%s".' % self.rx.invoice_status)

        # deliver completely
        pick = self.rx.picking_ids
        pick.move_ids.write({'quantity': 5, 'picked': True})
        pick.button_validate()

        # Check quantity delivered
        del_qty = sum(rxl.qty_delivered for rxl in self.rx.order_line)
        self.assertEqual(del_qty, 5.0, 'Prescription Stock: delivered quantity should be 5.0 instead of %s after complete delivery' % del_qty)

        # Check invoice
        self.assertEqual(self.rx.invoice_status, 'to invoice', 'Prescription Stock: rx invoice_status should be "to invoice" instead of "%s" before invoicing' % self.rx.invoice_status)
        self.inv_1 = self.rx._create_invoices()
        self.assertEqual(self.rx.invoice_status, 'invoiced', 'Prescription Stock: rx invoice_status should be "invoiced" instead of "%s" after invoicing' % self.rx.invoice_status)
        self.assertEqual(len(self.inv_1), 1, 'Prescription Stock: only one invoice instead of "%s" should be created' % len(self.inv_1))
        self.assertEqual(self.inv_1.amount_untaxed, self.inv_1.amount_untaxed, 'Prescription Stock: amount in RX and invoice should be the same')
        self.inv_1.action_post()

        # Create return picking
        stock_return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=pick.ids, active_id=pick.sorted().ids[0],
            active_model='stock.picking'))
        return_wiz = stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity = 2.0 # Return only 2
        return_wiz.product_return_moves.to_refund = True # Refund these 2
        res = return_wiz.create_returns()
        return_pick = self.env['stock.picking'].browse(res['res_id'])

        # Validate picking
        return_pick.move_ids.write({'quantity': 2, 'picked': True})
        return_pick.button_validate()

        # Check invoice
        self.assertEqual(self.rx.invoice_status, 'to invoice', 'Prescription Stock: rx invoice_status should be "to invoice" instead of "%s" after picking return' % self.rx.invoice_status)
        self.assertAlmostEqual(self.rx.order_line.sorted()[0].qty_delivered, 3.0, msg='Prescription Stock: delivered quantity should be 3.0 instead of "%s" after picking return' % self.rx.order_line.sorted()[0].qty_delivered)
        # let's do an invoice with refunds
        adv_wiz = self.env['prescriptions.advance.payment.inv'].with_context(active_ids=[self.rx.id]).create({
            'advance_payment_method': 'delivered',
        })
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.inv_2 = self.rx.invoice_ids.filtered(lambda r: r.state == 'draft')
        self.assertAlmostEqual(self.inv_2.invoice_line_ids.sorted()[0].quantity, 2.0, msg='Prescription Stock: refund quantity on the invoice should be 2.0 instead of "%s".' % self.inv_2.invoice_line_ids.sorted()[0].quantity)
        self.assertEqual(self.rx.invoice_status, 'no', 'Prescription Stock: rx invoice_status should be "no" instead of "%s" after invoicing the return' % self.rx.invoice_status)

    def test_04_create_picking_update_prescription_orderline(self):
        """
        Test that updating multiple prescriptions order lines after a successful delivery creates a single picking containing
        the new move lines.
        """
        # sell two products
        item1 = self.company_data['product_order_no']  # consumable
        item1.type = 'consu'
        item2 = self.company_data['product_delivery_no']    # storable
        item2.type = 'product'    # storable

        self.rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 1, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
                (0, 0, {'name': item2.name, 'product_id': item2.id, 'product_uom_qty': 1, 'product_uom': item2.uom_id.id, 'price_unit': item2.list_price}),
            ],
        })
        self.rx.action_confirm()

        # deliver them
        # One of the move is for a consumable product, thus is assigned. The second one is for a
        # storable product, thus is unavailable. Hitting `button_validate` will first ask to
        # process all the reserved quantities and, if the user chose to process, a second wizard
        # will ask to create a backorder for the unavailable product.
        self.assertEqual(len(self.rx.picking_ids), 1)
        res_dict = self.rx.picking_ids.sorted()[0].button_validate()
        wizard = Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        self.assertEqual(wizard._name, 'stock.backorder.confirmation')
        wizard.process()

        # Now, the original picking is done and there is a new one (the backorder).
        self.assertEqual(len(self.rx.picking_ids), 2)
        for picking in self.rx.picking_ids:
            move = picking.move_ids
            if picking.backorder_id:
                self.assertEqual(move.product_id.id, item2.id)
                self.assertEqual(move.state, 'confirmed')
            else:
                self.assertEqual(picking.move_ids.product_id.id, item1.id)
                self.assertEqual(move.state, 'sales')

        # update the two original prescriptions order lines
        self.rx.write({
            'order_line': [
                (1, self.rx.order_line.sorted()[0].id, {'product_uom_qty': 2}),
                (1, self.rx.order_line.sorted()[1].id, {'product_uom_qty': 2}),
            ]
        })
        # a single picking should be created for the new delivery
        self.assertEqual(len(self.rx.picking_ids), 2)
        backorder = self.rx.picking_ids.filtered(lambda p: p.backorder_id)
        self.assertEqual(len(backorder.move_ids), 2)
        for backorder_move in backorder.move_ids:
            if backorder_move.product_id.id == item1.id:
                self.assertEqual(backorder_move.product_qty, 1)
            elif backorder_move.product_id.id == item2.id:
                self.assertEqual(backorder_move.product_qty, 2)

        # add a new prescriptions order lines
        self.rx.write({
            'order_line': [
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 1, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
            ]
        })
        self.assertEqual(sum(backorder.move_ids.filtered(lambda m: m.product_id.id == item1.id).mapped('product_qty')), 2)

    def test_05_create_picking_update_prescription_orderline(self):
        """ Same test than test_04 but only with enough products in stock so that the reservation
        is successful.
        """
        # sell two products
        item1 = self.company_data['product_order_no']  # consumable
        item1.type = 'consu'  # consumable
        item2 = self.company_data['product_delivery_no']    # storable
        item2.type = 'product'    # storable

        self.env['stock.quant']._update_available_quantity(item2, self.company_data['default_warehouse'].lot_stock_id, 2)
        self.rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 1, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
                (0, 0, {'name': item2.name, 'product_id': item2.id, 'product_uom_qty': 1, 'product_uom': item2.uom_id.id, 'price_unit': item2.list_price}),
            ],
        })
        self.rx.action_confirm()

        # deliver them
        self.assertEqual(len(self.rx.picking_ids), 1)
        self.rx.picking_ids.sorted()[0].button_validate()
        self.assertEqual(self.rx.picking_ids.sorted()[0].state, "done")

        # update the two original prescriptions order lines
        self.rx.write({
            'order_line': [
                (1, self.rx.order_line.sorted()[0].id, {'product_uom_qty': 2}),
                (1, self.rx.order_line.sorted()[1].id, {'product_uom_qty': 2}),
            ]
        })
        # a single picking should be created for the new delivery
        self.assertEqual(len(self.rx.picking_ids), 2)

    def test_05_confirm_cancel_confirm(self):
        """ Confirm a prescriptions order, cancel it, set to quotation, change the
        partner, confirm it again: the second delivery order should have
        the new partner.
        """
        item1 = self.company_data['product_order_no']
        partner1 = self.partner_a.id
        partner2 = self.env['res.partner'].create({'name': 'Another Test Partner'})
        rx1 = self.env['prescriptions.order'].create({
            'partner_id': partner1,
            'order_line': [(0, 0, {
                'name': item1.name,
                'product_id': item1.id,
                'product_uom_qty': 1,
                'product_uom': item1.uom_id.id,
                'price_unit': item1.list_price,
            })],
        })
        rx1.action_confirm()
        self.assertEqual(len(rx1.picking_ids), 1)
        self.assertEqual(rx1.picking_ids.partner_id.id, partner1)
        rx1._action_cancel()
        rx1.action_draft()
        rx1.partner_id = partner2
        rx1.partner_shipping_id = partner2  # set by an onchange
        rx1.action_confirm()
        self.assertEqual(len(rx1.picking_ids), 2)
        picking2 = rx1.picking_ids.filtered(lambda p: p.state != 'cancel')
        self.assertEqual(picking2.partner_id.id, partner2.id)

    def test_06_uom(self):
        """ Sell a dozen of products stocked in units. Check that the quantities on the prescriptions order
        lines as well as the delivered quantities are handled in dozen while the moves themselves
        are handled in units. Edit the ordered quantities, check that the quantities are correctly
        updated on the moves. Edit the ir.config_parameter to propagate the uom of the prescriptions order
        lines to the moves and edit a last time the ordered quantities. Deliver, check the
        quantities.
        """
        uom_unit = self.env.ref('uom.product_uom_unit')
        uom_dozen = self.env.ref('uom.product_uom_dozen')
        item1 = self.company_data['product_order_no']

        self.assertEqual(item1.uom_id.id, uom_unit.id)

        # sell a dozen
        rx1 = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'name': item1.name,
                'product_id': item1.id,
                'product_uom_qty': 1,
                'product_uom': uom_dozen.id,
                'price_unit': item1.list_price,
            })],
        })
        rx1.action_confirm()

        # the move should be 12 units
        # note: move.product_qty = computed field, always in the uom of the quant
        #       move.product_uom_qty = stored field representing the initial demand in move.product_uom
        move1 = rx1.picking_ids.move_ids[0]
        self.assertEqual(move1.product_uom_qty, 12)
        self.assertEqual(move1.product_uom.id, uom_unit.id)
        self.assertEqual(move1.product_qty, 12)

        # edit the rx line, sell 2 dozen, the move should now be 24 units
        rx1.write({
            'order_line': [
                (1, rx1.order_line.id, {'product_uom_qty': 2}),
            ]
        })
        # The above will create a second move, and then the two moves will be merged in _merge_moves`
        # The picking moves are not well sorted because the new move has just been created, and this influences the resulting move,
        # in which move the twos are merged.
        # But, this doesn't seem really important which is the resulting move, but in this test we have to ensure
        # we use the resulting move to compare the qty.
        # ```
        # for moves in moves_to_merge:
        #     # link all move lines to record 0 (the one we will keep).
        #     moves.mapped('move_line_ids').write({'move_id': moves[0].id})
        #     # merge move data
        #     moves[0].write(moves._merge_moves_fields())
        #     # update merged moves dicts
        #     moves_to_unlink |= moves[1:]
        # ```
        move1 = rx1.picking_ids.move_ids[0]
        self.assertEqual(move1.product_uom_qty, 24)
        self.assertEqual(move1.product_uom.id, uom_unit.id)
        self.assertEqual(move1.product_qty, 24)

        # force the propagation of the uom, sell 3 dozen
        self.env['ir.config_parameter'].sudo().set_param('stock.propagate_uom', '1')
        rx1.write({
            'order_line': [
                (1, rx1.order_line.id, {'product_uom_qty': 3}),
            ]
        })
        move2 = rx1.picking_ids.move_ids.filtered(lambda m: m.product_uom.id == uom_dozen.id)
        self.assertEqual(move2.product_uom_qty, 1)
        self.assertEqual(move2.product_uom.id, uom_dozen.id)
        self.assertEqual(move2.product_qty, 12)

        # deliver everything
        move1.write({'quantity': 24, 'picked': True})
        move2.write({'quantity': 1, 'picked': True})
        rx1.picking_ids.button_validate()

        # check the delivered quantity
        self.assertEqual(rx1.order_line.qty_delivered, 3.0)

    def test_07_forced_qties(self):
        """ Make multiple prescriptions order lines of the same product which isn't available in stock. On
        the picking, create new move lines (through the detailed operations view). See that the move
        lines are correctly dispatched through the moves.
        """
        uom_unit = self.env.ref('uom.product_uom_unit')
        uom_dozen = self.env.ref('uom.product_uom_dozen')
        item1 = self.company_data['product_order_no']

        self.assertEqual(item1.uom_id.id, uom_unit.id)

        # sell a dozen
        rx1 = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': item1.name,
                    'product_id': item1.id,
                    'product_uom_qty': 1,
                    'product_uom': uom_dozen.id,
                    'price_unit': item1.list_price,
                }),
                (0, 0, {
                    'name': item1.name,
                    'product_id': item1.id,
                    'product_uom_qty': 1,
                    'product_uom': uom_dozen.id,
                    'price_unit': item1.list_price,
                }),
                (0, 0, {
                    'name': item1.name,
                    'product_id': item1.id,
                    'product_uom_qty': 1,
                    'product_uom': uom_dozen.id,
                    'price_unit': item1.list_price,
                }),
            ],
        })
        rx1.action_confirm()

        self.assertEqual(len(rx1.picking_ids.move_ids), 3)
        self.assertEqual(len(rx1.picking_ids.move_line_ids), 3)
        rx1.picking_ids.move_ids.picked = True
        rx1.picking_ids.button_validate()
        self.assertEqual(rx1.picking_ids.state, 'sales')
        self.assertEqual(rx1.order_line.mapped('qty_delivered'), [1, 1, 1])

    def test_08_quantities(self):
        """Change the picking code of the receipts to internal. Make a RX for 10 units, go to the
        picking and return 5, edit the RX line to 15 units.

        The purpose of the test is to check the consistencies across the delivered quantities and the
        procurement quantities.
        """
        # Change the code of the picking type receipt
        self.env['stock.picking.type'].search([('code', '=', 'incoming')]).write({'code': 'internal'})

        # Sell and deliver 10 units
        item1 = self.company_data['product_order_no']
        uom_unit = self.env.ref('uom.product_uom_unit')
        rx1 = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': item1.name,
                    'product_id': item1.id,
                    'product_uom_qty': 10,
                    'product_uom': uom_unit.id,
                    'price_unit': item1.list_price,
                }),
            ],
        })
        rx1.action_confirm()

        picking = rx1.picking_ids
        picking.button_validate()

        # Return 5 units
        stock_return_picking_form = Form(self.env['stock.return.picking'].with_context(
            active_ids=picking.ids,
            active_id=picking.sorted().ids[0],
            active_model='stock.picking'
        ))
        return_wiz = stock_return_picking_form.save()
        for return_move in return_wiz.product_return_moves:
            return_move.write({
                'quantity': 5,
                'to_refund': True
            })
        res = return_wiz.create_returns()
        return_pick = self.env['stock.picking'].browse(res['res_id'])
        return_pick.button_validate()

        self.assertEqual(rx1.order_line.qty_delivered, 5)

        # Deliver 15 instead of 10.
        rx1.write({
            'order_line': [
                (1, rx1.order_line.sorted()[0].id, {'product_uom_qty': 15}),
            ]
        })

        # A new move of 10 unit (15 - 5 units)
        self.assertEqual(rx1.order_line.qty_delivered, 5)
        self.assertEqual(rx1.picking_ids.sorted('id')[-1].move_ids.product_qty, 10)

    def test_09_qty_available(self):
        """ create a prescriptions order in warehouse1, change to warehouse2 and check the
        available quantities on prescriptions order lines are well updated """
        # sell two products
        item1 = self.company_data['product_order_no']
        item1.type = 'product'

        warehouse1 = self.company_data['default_warehouse']
        self.env['stock.quant']._update_available_quantity(item1, warehouse1.lot_stock_id, 10)
        self.env['stock.quant']._update_reserved_quantity(item1, warehouse1.lot_stock_id, 3)

        warehouse2 = self.env['stock.warehouse'].create({
            'partner_id': self.partner_a.id,
            'name': 'Zizizatestwarehouse',
            'code': 'Test',
        })
        self.env['stock.quant']._update_available_quantity(item1, warehouse2.lot_stock_id, 5)
        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 1, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
            ],
        })
        line = rx.order_line[0]
        self.assertAlmostEqual(line.scheduled_date, datetime.now(), delta=timedelta(seconds=10))
        self.assertEqual(line.virtual_available_at_date, 10)
        self.assertEqual(line.free_qty_today, 7)
        self.assertEqual(line.qty_available_today, 10)
        self.assertEqual(line.pod_warehouse_id, warehouse1)
        self.assertEqual(line.qty_to_deliver, 1)
        rx.pod_warehouse_id = warehouse2
        # invalidate product cache to ensure qty_available is recomputed
        # bc warehouse isn't in the depends_context of qty_available
        self.env.invalidate_all()
        self.assertEqual(line.virtual_available_at_date, 5)
        self.assertEqual(line.free_qty_today, 5)
        self.assertEqual(line.qty_available_today, 5)
        self.assertEqual(line.pod_warehouse_id, warehouse2)
        self.assertEqual(line.qty_to_deliver, 1)

    def test_10_qty_available(self):
        """create a prescriptions order containing three times the same product. The
        quantity available should be different for the 3 lines"""
        item1 = self.company_data['product_order_no']
        item1.type = 'product'
        self.env['stock.quant']._update_available_quantity(item1, self.company_data['default_warehouse'].lot_stock_id, 10)
        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 5, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 5, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
                (0, 0, {'name': item1.name, 'product_id': item1.id, 'product_uom_qty': 5, 'product_uom': item1.uom_id.id, 'price_unit': item1.list_price}),
            ],
        })
        self.assertEqual(rx.order_line.mapped('free_qty_today'), [10, 5, 0])

    def test_11_return_with_refund(self):
        """ Creates a prescriptions order, valids it and its delivery, then creates a
        return. The return must refund by default and the prescriptions order delivered
        quantity must be updated.
        """
        # Creates a prescriptions order for 10 products.
        prescriptions_order = self._get_new_prescriptions_order()
        # Valids the prescriptions order, then valids the delivery.
        prescriptions_order.action_confirm()
        self.assertTrue(prescriptions_order.picking_ids)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)
        picking = prescriptions_order.picking_ids
        picking.move_ids.write({'quantity': 10, 'picked': True})
        picking.button_validate()

        # Checks the delivery amount (must be 10).
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 10)
        # Creates a return from the delivery picking.
        return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.id,
            active_model='stock.picking'))
        return_wizard = return_picking_form.save()
        # Checks the field `to_refund` is checked (must be checked by default).
        self.assertEqual(return_wizard.product_return_moves.to_refund, True)
        self.assertEqual(return_wizard.product_return_moves.quantity, 10)

        # Valids the return picking.
        res = return_wizard.create_returns()
        return_picking = self.env['stock.picking'].browse(res['res_id'])
        return_picking.move_ids.write({'quantity': 10, 'picked': True})
        return_picking.button_validate()
        # Checks the delivery amount (must be 0).
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)

    def test_12_return_without_refund(self):
        """ Do the exact thing than in `test_11_return_with_refund` except we
        set on False the refund and checks the prescriptions order delivered quantity
        isn't changed.
        """
        # Creates a prescriptions order for 10 products.
        prescriptions_order = self._get_new_prescriptions_order()
        # Valids the prescriptions order, then valids the delivery.
        prescriptions_order.action_confirm()
        self.assertTrue(prescriptions_order.picking_ids)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)
        picking = prescriptions_order.picking_ids
        picking.move_ids.write({'quantity': 10, 'picked': True})
        picking.button_validate()

        # Checks the delivery amount (must be 10).
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 10)
        # Creates a return from the delivery picking.
        return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.id,
            active_model='stock.picking'))
        return_wizard = return_picking_form.save()
        # Checks the field `to_refund` is checked, then unchecks it.
        self.assertEqual(return_wizard.product_return_moves.to_refund, True)
        self.assertEqual(return_wizard.product_return_moves.quantity, 10)
        return_wizard.product_return_moves.to_refund = False
        # Valids the return picking.
        res = return_wizard.create_returns()
        return_picking = self.env['stock.picking'].browse(res['res_id'])
        return_picking.move_ids.write({'quantity': 10, 'picked': True})
        return_picking.button_validate()
        # Checks the delivery amount (must still be 10).
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 10)

    def test_13_delivered_qty(self):
        """ Creates a prescriptions order, valids it and adds a new move line in the delivery for a
        product with an invoicing policy on 'order', then checks a new RX line was created.
        After that, creates a second prescriptions order and does the same thing but with a product
        with and invoicing policy on 'ordered'.
        """
        product_inv_on_delivered = self.company_data['product_delivery_no']
        # Configure a product with invoicing policy on order.
        product_inv_on_order = self.env['product.product'].create({
            'name': 'Shenaniffluffy',
            'type': 'consu',
            'invoice_policy': 'order',
            'list_price': 55.0,
        })
        # Creates a prescriptions order for 3 products invoiced on qty. delivered.
        prescriptions_order = self._get_new_prescriptions_order(amount=3)
        # Confirms the prescriptions order, then increases the delivered qty., adds a new
        # line and valids the delivery.
        prescriptions_order.action_confirm()
        self.assertTrue(prescriptions_order.picking_ids)
        self.assertEqual(len(prescriptions_order.order_line), 1)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)
        picking = prescriptions_order.picking_ids
        initial_product = prescriptions_order.order_line.product_id

        picking_form = Form(picking)
        with picking_form.move_line_ids_without_package.edit(0) as move:
            move.quantity = 5
        with picking_form.move_line_ids_without_package.new() as new_move:
            new_move.product_id = product_inv_on_order
            new_move.quantity = 5
        picking = picking_form.save()
        picking.move_ids.picked = True
        picking.button_validate()

        # Check a new prescriptions order line was correctly created.
        self.assertEqual(len(prescriptions_order.order_line), 2)
        rx_line_1 = prescriptions_order.order_line[0]
        rx_line_2 = prescriptions_order.order_line[1]
        self.assertEqual(rx_line_1.product_id.id, product_inv_on_delivered.id)
        self.assertEqual(rx_line_1.product_uom_qty, 3)
        self.assertEqual(rx_line_1.qty_delivered, 5)
        self.assertEqual(rx_line_1.price_unit, 70.0)
        self.assertEqual(rx_line_2.product_id.id, product_inv_on_order.id)
        self.assertEqual(rx_line_2.product_uom_qty, 0)
        self.assertEqual(rx_line_2.qty_delivered, 5)
        self.assertEqual(
            rx_line_2.price_unit, 0,
            "Shouldn't get the product price as the invoice policy is on qty. ordered")

        # Check the picking didn't change
        self.assertRecordValues(prescriptions_order.picking_ids.move_ids, [
            {'product_id': initial_product.id, 'quantity': 5},
            {'product_id': product_inv_on_order.id, 'quantity': 5},
        ])

        # Creates a second prescriptions order for 3 product invoiced on qty. ordered.
        prescriptions_order = self._get_new_prescriptions_order(product=product_inv_on_order, amount=3)
        # Confirms the prescriptions order, then increases the delivered qty., adds a new
        # line and valids the delivery.
        prescriptions_order.action_confirm()
        self.assertTrue(prescriptions_order.picking_ids)
        self.assertEqual(len(prescriptions_order.order_line), 1)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)
        picking = prescriptions_order.picking_ids

        picking_form = Form(picking)
        with picking_form.move_line_ids_without_package.edit(0) as move:
            move.quantity = 5
        with picking_form.move_line_ids_without_package.new() as new_move:
            new_move.product_id = product_inv_on_delivered
            new_move.quantity = 5
        picking = picking_form.save()
        picking.move_ids.picked = True
        picking.button_validate()

        # Check a new prescriptions order line was correctly created.
        self.assertEqual(len(prescriptions_order.order_line), 2)
        rx_line_1 = prescriptions_order.order_line[0]
        rx_line_2 = prescriptions_order.order_line[1]
        self.assertEqual(rx_line_1.product_id.id, product_inv_on_order.id)
        self.assertEqual(rx_line_1.product_uom_qty, 3)
        self.assertEqual(rx_line_1.qty_delivered, 5)
        self.assertEqual(rx_line_1.price_unit, 55.0)
        self.assertEqual(rx_line_2.product_id.id, product_inv_on_delivered.id)
        self.assertEqual(rx_line_2.product_uom_qty, 0)
        self.assertEqual(rx_line_2.qty_delivered, 5)
        self.assertEqual(
            rx_line_2.price_unit, 70.0,
            "Should get the product price as the invoice policy is on qty. delivered")

    def test_14_delivered_qty_in_multistep(self):
        """ Creates a prescriptions order with delivery in two-step. Process the pick &
        ship and check we don't have extra RX line. Then, do the same but with
        adding a extra move and check only one extra RX line was created.
        """
        # Set the delivery in two steps.
        warehouse = self.company_data['default_warehouse']
        warehouse.delivery_steps = 'pick_ship'
        # Configure a product with invoicing policy on order.
        product_inv_on_order = self.env['product.product'].create({
            'name': 'Shenaniffluffy',
            'type': 'consu',
            'invoice_policy': 'order',
            'list_price': 55.0,
        })
        # Create a prescriptions order.
        prescriptions_order = self._get_new_prescriptions_order()
        # Confirms the prescriptions order, then valids pick and delivery.
        prescriptions_order.action_confirm()
        self.assertTrue(prescriptions_order.picking_ids)
        self.assertEqual(len(prescriptions_order.order_line), 1)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)
        pick = prescriptions_order.picking_ids.filtered(lambda p: p.picking_type_code == 'internal')
        delivery = prescriptions_order.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing')

        picking_form = Form(pick)
        with picking_form.move_line_ids_without_package.edit(0) as move:
            move.quantity = 10
        pick = picking_form.save()
        pick.move_ids.picked = True
        pick.button_validate()

        picking_form = Form(delivery)
        with picking_form.move_line_ids_without_package.edit(0) as move:
            move.quantity = 10
        delivery = picking_form.save()
        delivery.move_ids.picked = True
        delivery.button_validate()

        # Check no new prescriptions order line was created.
        self.assertEqual(len(prescriptions_order.order_line), 1)
        self.assertEqual(prescriptions_order.order_line.product_uom_qty, 10)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 10)
        self.assertEqual(prescriptions_order.order_line.price_unit, 70.0)

        # Creates a second prescriptions order.
        prescriptions_order = self._get_new_prescriptions_order()
        # Confirms the prescriptions order then add a new line for an another product in the pick/out.
        prescriptions_order.action_confirm()
        self.assertTrue(prescriptions_order.picking_ids)
        self.assertEqual(len(prescriptions_order.order_line), 1)
        self.assertEqual(prescriptions_order.order_line.qty_delivered, 0)
        pick = prescriptions_order.picking_ids.filtered(lambda p: p.picking_type_code == 'internal')
        delivery = prescriptions_order.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing')

        picking_form = Form(pick)
        with picking_form.move_line_ids_without_package.edit(0) as move:
            move.quantity = 10
        with picking_form.move_line_ids_without_package.new() as new_move:
            new_move.product_id = product_inv_on_order
            new_move.quantity = 10
        pick = picking_form.save()
        pick.move_ids.picked = True
        pick.button_validate()

        picking_form = Form(delivery)
        with picking_form.move_line_ids_without_package.edit(0) as move:
            move.quantity = 10
        with picking_form.move_line_ids_without_package.new() as new_move:
            new_move.product_id = product_inv_on_order
            new_move.quantity = 10
        delivery = picking_form.save()
        delivery.move_ids.picked = True
        delivery.button_validate()

        # Check a new prescriptions order line was correctly created.
        self.assertEqual(len(prescriptions_order.order_line), 2)
        rx_line_1 = prescriptions_order.order_line[0]
        rx_line_2 = prescriptions_order.order_line[1]
        self.assertEqual(rx_line_1.product_id.id, self.company_data['product_delivery_no'].id)
        self.assertEqual(rx_line_1.product_uom_qty, 10)
        self.assertEqual(rx_line_1.qty_delivered, 10)
        self.assertEqual(rx_line_1.price_unit, 70.0)
        self.assertEqual(rx_line_2.product_id.id, product_inv_on_order.id)
        self.assertEqual(rx_line_2.product_uom_qty, 0)
        self.assertEqual(rx_line_2.qty_delivered, 10)
        self.assertEqual(rx_line_2.price_unit, 0)

    def test_08_prescriptions_return_qty_and_cancel(self):
        """
        Test a RX with a product on delivery with a 5 quantity.
        Create two invoices: one for 3 quantity and one for 2 quantity
        Then cancel Prescription order, it won't raise any warning, it should be cancelled.
        """
        partner = self.partner_a
        product = self.company_data['product_delivery_no']
        rx_vals = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 5.0,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price})],
            'pricelist_id': self.company_data['default_pricelist'].id,
        }
        rx = self.env['prescriptions.order'].create(rx_vals)

        # confirm the rx
        rx.action_confirm()

        # deliver partially
        pick = rx.picking_ids
        pick.move_ids.write({'quantity': 3, 'picked': True})

        wiz_act = pick.button_validate()
        wiz = Form(self.env[wiz_act['res_model']].with_context(wiz_act['context'])).save()
        wiz.process()

        # create invoice for 3 quantity and post it
        inv_1 = rx._create_invoices()
        inv_1.action_post()
        self.assertEqual(inv_1.state, 'posted', 'invoice should be in posted state')

        pick_2 = rx.picking_ids.filtered('backorder_id')
        pick_2.move_ids.write({'quantity': 2, 'picked': True})
        pick_2.button_validate()

        # create invoice for remaining 2 quantity
        inv_2 = rx._create_invoices()
        self.assertEqual(inv_2.state, 'draft', 'invoice should be in draft state')

        # check the status of invoices after cancelling the order
        rx._action_cancel()
        wizard = self.env['prescriptions.order.cancel'].with_context({'order_id': rx.id}).create({'order_id': rx.id})
        wizard.action_cancel()
        self.assertEqual(inv_1.state, 'posted', 'A posted invoice state should remain posted')
        self.assertEqual(inv_2.state, 'cancel', 'A drafted invoice state should be cancelled')

    def test_reservation_method_w_prescription(self):
        picking_type_out = self.company_data['default_warehouse'].out_type_id
        # make sure generated picking will auto-assign
        picking_type_out.reservation_method = 'at_confirm'
        product = self.company_data['product_delivery_no']
        product.type = 'product'
        self.env['stock.quant']._update_available_quantity(product, self.company_data['default_warehouse'].lot_stock_id, 20)

        prescriptions_order1 = self._get_new_prescriptions_order(amount=10.0)
        # Validate the prescriptions order, picking should automatically assign stock
        prescriptions_order1.action_confirm()
        picking1 = prescriptions_order1.picking_ids
        self.assertTrue(picking1)
        self.assertEqual(picking1.state, 'assigned')
        picking1.unlink()

        # make sure generated picking will does not auto-assign
        picking_type_out.reservation_method = 'manual'
        prescriptions_order2 = self._get_new_prescriptions_order(amount=10.0)
        # Validate the prescriptions order, picking should not automatically assign stock
        prescriptions_order2.action_confirm()
        picking2 = prescriptions_order2.picking_ids
        self.assertTrue(picking2)
        self.assertEqual(picking2.state, 'confirmed')
        picking2.unlink()

        # make sure generated picking auto-assigns according to (picking) scheduled date
        picking_type_out.reservation_method = 'by_date'
        picking_type_out.reservation_days_before = 2
        # too early for scheduled date => don't auto-assign
        prescriptions_order3 = self._get_new_prescriptions_order(amount=10.0)
        prescriptions_order3.commitment_date = datetime.now() + timedelta(days=10)
        prescriptions_order3.action_confirm()
        picking3 = prescriptions_order3.picking_ids
        self.assertTrue(picking3)
        self.assertEqual(picking3.state, 'confirmed')
        picking3.unlink()
        # within scheduled date + reservation days before => auto-assign
        prescriptions_order4 = self._get_new_prescriptions_order(amount=10.0)
        prescriptions_order4.commitment_date = datetime.now() + timedelta(days=1)
        prescriptions_order4.action_confirm()
        self.assertTrue(prescriptions_order4.picking_ids)
        self.assertEqual(prescriptions_order4.picking_ids.state, 'assigned')

    def test_packaging_propagation(self):
        """Create a RX with lines using packaging, check the packaging propagate
        to its move.
        """
        warehouse = self.company_data['default_warehouse']
        warehouse.delivery_steps = 'pick_pack_ship'
        product = self.env['product.product'].create({
            'name': 'Product with packaging',
            'type': 'product',
        })

        packOf10 = self.env['product.packaging'].create({
            'name': 'PackOf10',
            'product_id': product.id,
            'qty': 10
        })

        packOf20 = self.env['product.packaging'].create({
            'name': 'PackOf20',
            'product_id': product.id,
            'qty': 20
        })

        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': 10.0,
                    'product_uom': product.uom_id.id,
                    'product_packaging_id': packOf10.id,
                })],
        })
        rx.action_confirm()
        pick = rx.order_line.move_ids
        pack = pick.move_orig_ids
        ship = pack.move_orig_ids
        self.assertEqual(pick.product_packaging_id, packOf10)
        self.assertEqual(pack.product_packaging_id, packOf10)
        self.assertEqual(ship.product_packaging_id, packOf10)

        rx.order_line[0].write({
            'product_packaging_id': packOf20.id,
            'product_uom_qty': 20
        })
        self.assertEqual(rx.order_line.move_ids.product_packaging_id, packOf20)
        self.assertEqual(pick.product_packaging_id, packOf20)
        self.assertEqual(pack.product_packaging_id, packOf20)
        self.assertEqual(ship.product_packaging_id, packOf20)

        rx.order_line[0].write({'product_packaging_id': False})
        self.assertFalse(pick.product_packaging_id)
        self.assertFalse(pack.product_packaging_id)
        self.assertFalse(ship.product_packaging_id)

    def test_15_cancel_delivery(self):
        """ Suppose the option "Lock Confirmed Prescriptions" enabled and a product with the invoicing
        policy set to "Delivered quantities". When cancelling the delivery of such a product, the
        invoice status of the associated RX should be 'Nothing to Invoice'
        """
        group_auto_done = self.env.ref('pod_prescriptions.group_auto_done_setting')
        self.env.user.groups_id = [(4, group_auto_done.id)]

        product = self.product_a
        product.invoice_policy = 'delivery'
        partner = self.partner_a
        rx = self.env['prescriptions.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 2,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price
            })],
        })
        rx.action_confirm()
        self.assertEqual(rx.state, 'sales')
        self.assertTrue(rx.locked)
        rx.picking_ids.action_cancel()

        self.assertEqual(rx.invoice_status, 'no')

    def test_16_multi_uom(self):
        yards_uom = self.env['uom.uom'].create({
            'category_id': self.env.ref('uom.uom_categ_length').id,
            'name': 'Yards',
            'factor_inv': 0.9144,
            'uom_type': 'bigger',
        })
        product = self.env.ref('product.product_product_11').copy({
            'uom_id': self.env.ref('uom.product_uom_meter').id,
            'uom_po_id': yards_uom.id,
        })
        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': 4.0,
                    'product_uom': yards_uom.id,
                    'price_unit': 1.0,
                })
            ],
        })
        rx.action_confirm()
        picking = rx.picking_ids[0]
        picking.move_ids.write({'quantity': 3.66, 'picked': True})
        picking.button_validate()
        self.assertEqual(rx.order_line.mapped('qty_delivered'), [4.0], 'Prescription: no conversion error on delivery in different uom"')

    def test_17_qty_update_propagation(self):
        """ Creates a prescriptions order, then modifies the prescriptions order lines qty and verifies
        that quantity changes are correctly propagated to the picking and delivery picking.
        """
        # Set the delivery in two steps.
        warehouse = self.company_data['default_warehouse']
        warehouse.delivery_steps = 'pick_ship'
        # Sell a product.
        product = self.company_data['product_delivery_no']    # storable
        product.type = 'product'    # storable

        self.env['stock.quant']._update_available_quantity(product, self.company_data['default_warehouse'].lot_stock_id, 50)
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {'name': product.name, 'product_id': product.id, 'product_uom_qty': 50, 'product_uom': product.uom_id.id, 'price_unit': product.list_price}),
            ],
        })
        prescriptions_order.action_confirm()

        # Check picking created
        self.assertEqual(len(prescriptions_order.picking_ids), 2, 'A picking and a delivery picking should have been created.')
        customer_location = self.env.ref('stock.stock_location_customers')
        move_pick = prescriptions_order.picking_ids.filtered(lambda p: p.location_dest_id.id != customer_location.id).move_ids
        move_out = prescriptions_order.picking_ids.filtered(lambda p: p.location_dest_id.id == customer_location.id).move_ids
        self.assertEqual(len(move_out), 1, 'Only one move should be created for a single product.')
        self.assertEqual(move_out.product_uom_qty, 50, 'The move quantity should be the same as the quantity sold.')

        # Decrease the quantity in the prescriptions order and check the move has been updated.
        prescriptions_order.write({
            'order_line': [
                (1, prescriptions_order.order_line.id, {'product_uom_qty': 30}),
            ]
        })
        self.assertEqual(move_pick.product_uom_qty, 30, 'The move quantity should have been decreased as the prescriptions order line was.')
        self.assertEqual(move_out.product_uom_qty, 30, 'The move quantity should have been decreased as the prescriptions order line and the pick line were.')
        self.assertEqual(len(prescriptions_order.picking_ids), 2, 'No additionnal picking should have been created.')

        # Increase the quantity in the prescriptions order and check the move has been updated.
        prescriptions_order.write({
            'order_line': [
                (1, prescriptions_order.order_line.id, {'product_uom_qty': 40})
            ]
        })
        self.assertEqual(move_pick.product_uom_qty, 40, 'The move quantity should have been increased as the prescriptions order line was.')
        self.assertEqual(move_out.product_uom_qty, 40, 'The move quantity should have been increased as the prescriptions order line and the pick line were.')

    def test_18_deliver_more_and_multi_uom(self):
        """
        Deliver an additional product with a UoM different than its default one
        This UoM should be the same on the generated RX line
        """
        uom_m_id = self.ref("uom.product_uom_meter")
        uom_km_id = self.ref("uom.product_uom_km")
        self.product_b.write({
            'uom_id': uom_m_id,
            'uom_po_id': uom_m_id,
        })

        rx = self._get_new_prescriptions_order(product=self.product_a)
        rx.action_confirm()

        picking = rx.picking_ids
        self.env['stock.move'].create({
            'picking_id': picking.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'name': self.product_b.name,
            'product_id': self.product_b.id,
            'product_uom_qty': 1,
            'product_uom': uom_km_id,
            'quantity': 1,
        })
        picking.button_validate()

        self.assertEqual(rx.order_line[1].product_id, self.product_b)
        self.assertEqual(rx.order_line[1].qty_delivered, 1)
        self.assertEqual(rx.order_line[1].product_uom.id, uom_km_id)

    def test_19_deliver_update_rx_line_qty(self):
        """
        Creates a prescriptions order, then validates the delivery
        modifying the prescriptions order lines qty via import and ensures
        a new delivery is created.
        """
        self.product_a.type = 'product'
        self.env['stock.quant']._update_available_quantity(
            self.product_a, self.company_data['default_warehouse'].lot_stock_id, 10)

        # Create prescriptions order
        prescriptions_order = self._get_new_prescriptions_order()
        prescriptions_order.action_confirm()

        # Validate delivery
        picking = prescriptions_order.picking_ids
        picking.move_ids.write({'quantity': 10, 'picked': True})
        picking.button_validate()

        # Update the line and check a new delivery is created
        with Form(prescriptions_order.with_context(import_file=True)) as rx_form:
            with rx_form.order_line.edit(0) as line:
                line.product_uom_qty = 777

        self.assertEqual(len(prescriptions_order.picking_ids), 2)

    def test_multiple_returns(self):
        # Creates a prescriptions order for 10 products.
        prescriptions_order = self._get_new_prescriptions_order()
        # Valids the prescriptions order, then valids the delivery.
        prescriptions_order.action_confirm()
        picking = prescriptions_order.picking_ids
        picking.move_ids.write({'quantity': 10, 'picked': True})
        picking.button_validate()

        # Creates a return from the delivery picking.
        return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.id,
            active_model='stock.picking'))
        return_wizard = return_picking_form.save()
        # Check that the correct quantity is set on the retrun
        self.assertEqual(return_wizard.product_return_moves.quantity, 10)
        return_wizard.product_return_moves.quantity = 2
        # Valids the return picking.
        res = return_wizard.create_returns()
        return_picking = self.env['stock.picking'].browse(res['res_id'])
        return_picking.move_ids.write({'quantity': 2, 'picked': True})
        return_picking.button_validate()

        # Creates a second return from the delivery picking.
        return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.id,
            active_model='stock.picking'))
        return_wizard = return_picking_form.save()
        # Check that the remaining quantity is set on the retrun
        self.assertEqual(return_wizard.product_return_moves.quantity, 8)

    def test_return_with_mto_and_multisteps(self):
        """
        Suppose a product P and a 3-steps delivery.
        Sell 5 x P, process pick & pack pickings and then decrease the qty on
        the RX line:
        - the ship picking should be updated
        - there should be a return R1 for the pack picking
        - there should be a return R2 for the pick picking
        - it should be possible to reserve R1
        """
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        warehouse.delivery_steps = 'pick_pack_ship'
        stock_location = warehouse.lot_stock_id
        pack_location, out_location, custo_location = warehouse.delivery_route_id.rule_ids.location_dest_id

        product = self.env['product.product'].create({
            'name': 'SuperProduct',
            'type': 'product',
        })

        self.env['stock.quant']._update_available_quantity(product, stock_location, 5)

        rx_form = Form(self.env['prescriptions.order'])
        rx_form.partner_id = self.partner_a
        with rx_form.order_line.new() as line:
            line.product_id = product
            line.product_uom_qty = 5
        rx = rx_form.save()
        rx.action_confirm()

        _, pack_picking, pick_picking = rx.picking_ids
        (pick_picking + pack_picking).move_ids.write({'quantity': 5, 'picked': True})
        (pick_picking + pack_picking).button_validate()
        with Form(rx) as rx_form:
            with rx_form.order_line.edit(0) as line:
                line.product_uom_qty = 3

        move_lines = rx.picking_ids.move_ids.sorted('id')
        ship_sm, pack_sm, pick_sm, ret_pack_sm, ret_pick_sm = move_lines
        self.assertRecordValues(move_lines, [
            {'location_id': out_location.id, 'location_dest_id': custo_location.id, 'move_orig_ids': pack_sm.ids, 'move_dest_ids': []},
            {'location_id': pack_location.id, 'location_dest_id': out_location.id, 'move_orig_ids': pick_sm.ids, 'move_dest_ids': ship_sm.ids},
            {'location_id': stock_location.id, 'location_dest_id': pack_location.id, 'move_orig_ids': [], 'move_dest_ids': pack_sm.ids},
            {'location_id': out_location.id, 'location_dest_id': pack_location.id, 'move_orig_ids': [], 'move_dest_ids': ret_pick_sm.ids},
            {'location_id': pack_location.id, 'location_dest_id': stock_location.id, 'move_orig_ids': ret_pack_sm.ids, 'move_dest_ids': []},
        ])

        ret_pack_sm.picking_id.action_assign()
        self.assertEqual(ret_pack_sm.state, 'assigned')
        self.assertEqual(ret_pack_sm.move_line_ids.quantity, 2)

    def test_mtrx_and_qty_decreasing(self):
        """
        First, confirm a RX that has a line with the MTO route (the product
        should already be available in stock). Then, decrease the qty on the RX
        line:
        - The delivery should be updated
        - There should not be any other picking
        """
        warehouse = self.company_data['default_warehouse']
        customer_location = self.env.ref('stock.stock_location_customers')
        mto_route = self.env.ref('stock.route_warehouse0_mto')
        mto_route.active = True

        self.product_a.type = 'product'
        self.env['stock.quant']._update_available_quantity(self.product_a, warehouse.lot_stock_id, 10)

        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'pod_warehouse_id': warehouse.id,
            'order_line': [(0, 0, {
                'name': self.product_a.name,
                'product_id': self.product_a.id,
                'product_uom_qty': 10,
                'product_uom': self.product_a.uom_id.id,
                'price_unit': 1,
                'route_id': mto_route.id,
            })],
        })
        rx.action_confirm()
        self.assertRecordValues(rx.picking_ids, [{'location_id': warehouse.lot_stock_id.id, 'location_dest_id': customer_location.id}])

        rx.order_line.product_uom_qty = 8
        self.assertRecordValues(rx.picking_ids, [{'location_id': warehouse.lot_stock_id.id, 'location_dest_id': customer_location.id}])
        self.assertEqual(rx.picking_ids.move_ids.product_uom_qty, 8)

    def test_packaging_and_qty_decrease(self):
        packaging = self.env['product.packaging'].create({
            'name': "Super Packaging",
            'product_id': self.product_a.id,
            'qty': 10.0,
        })

        rx_form = Form(self.env['prescriptions.order'])
        rx_form.partner_id = self.partner_a
        with rx_form.order_line.new() as line:
            line.product_id = self.product_a
            line.product_uom_qty = 10
        rx = rx_form.save()
        rx.action_confirm()

        self.assertEqual(rx.order_line.product_packaging_id, packaging)

        with Form(rx) as rx_form:
            with rx_form.order_line.edit(0) as line:
                line.product_uom_qty = 8

        self.assertEqual(rx.picking_ids.move_ids.product_uom_qty, 8)

    def test_backorder_and_decrease_rxl_qty(self):
        """
        2 steps delivery
        RX with 10 x P
        Process pickings of 6 x P with backorders
        Update RX: 7 x P
        Backorder should be updated: 1 x P
        """
        warehouse = self.company_data['default_warehouse']
        warehouse.delivery_steps = 'pick_ship'
        stock_location = warehouse.lot_stock_id
        out_location = warehouse.wh_output_stock_loc_id
        customer_location = self.env.ref('stock.stock_location_customers')

        rx = self._get_new_prescriptions_order()
        rx.action_confirm()
        pick01, ship01 = rx.picking_ids

        pick01.move_line_ids.write({'quantity': 6})
        pick01.move_ids.picked = True
        pick01._action_done()
        pick02 = pick01.backorder_ids

        ship01.move_ids.write({'quantity': 6, 'picked': True})
        ship01._action_done()
        ship02 = ship01.backorder_ids

        rx.order_line.product_uom_qty = 7

        self.assertRecordValues(rx.picking_ids.move_ids.sorted('id'), [
            {'location_id': out_location.id, 'location_dest_id': customer_location.id, 'product_uom_qty': 6.0, 'quantity': 6.0, 'state': 'sales'},
            {'location_id': stock_location.id, 'location_dest_id': out_location.id, 'product_uom_qty': 6.0, 'quantity': 6.0, 'state': 'sales'},
            {'location_id': stock_location.id, 'location_dest_id': out_location.id, 'product_uom_qty': 1.0, 'quantity': 1.0, 'state': 'assigned'},
            {'location_id': out_location.id, 'location_dest_id': customer_location.id, 'product_uom_qty': 1.0, 'quantity': 0.0, 'state': 'waiting'},
        ])
        self.assertEqual(ship01.move_ids.move_orig_ids, (pick01 | pick02).move_ids)
        self.assertEqual(ship02.move_ids.move_orig_ids, (pick01 | pick02).move_ids)

    def test_incoterm_in_advance_payment(self):
        """When generating a advance payment invoice from a RX, this invoice incoterm should be the same as the RX"""

        incoterm = self.env['account.incoterms'].create({
            'name': 'Test Incoterm',
            'code': 'TEST',
        })

        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'incoterm': incoterm.id,
            'order_line': [(0, 0, {
                'name': self.product_a.name,
                'product_id': self.product_a.id,
                'product_uom_qty': 10,
                'product_uom': self.product_a.uom_id.id,
                'price_unit': 1,
            })],
        })
        rx.action_confirm()

        advance_product = self.env['product.product'].create({
            'name': 'Deposit',
            'type': 'service',
            'invoice_policy': 'order',
        })

        adv_wiz = self.env['prescriptions.advance.payment.inv'].with_context(active_ids=[rx.id]).create({
            'advance_payment_method': 'percentage',
            'amount': 5.0,
            'product_id': advance_product.id,
        })

        act = adv_wiz.with_context(open_invoices=True).create_invoices()
        invoice = self.env['account.move'].browse(act['res_id'])

        self.assertEqual(invoice.invoice_incoterm_id.id, incoterm.id)

    def test_exception_delivery_partial_multi(self):
        """
        When a backorder is cancelled for a picking in multi-picking,
        the related RX should have an exception logged
        """
        #Create 2 prescriptions orders
        rx_1 = self._get_new_prescriptions_order()
        rx_1.action_confirm()
        picking_1 = rx_1.picking_ids
        picking_1.move_ids.write({'quantity': 1, 'picked': True})

        rx_2 = self._get_new_prescriptions_order()
        rx_2.action_confirm()
        picking_2 = rx_2.picking_ids
        picking_2.move_ids.write({'quantity': 2, 'picked': True})

        #multi-picking validation
        pick = picking_1 | picking_2
        res_dict = pick.button_validate()
        wizard = Form(self.env[(res_dict.get('res_model'))].with_context(res_dict['context'])).save()
        wizard.backorder_confirmation_line_ids[1].write({'to_backorder': False})
        wizard.process()

        #Check Exception error is logged on rx_2
        activity = self.env['mail.activity'].search([('res_id', '=', rx_2.id), ('res_model', '=', 'prescriptions.order')])
        self.assertEqual(len(activity), 1, 'When no backorder is created for a partial delivery, a warning error should be logged in its origin RX')

    def test_3_steps_and_unpack(self):
        """
        When removing the package of a stock.move.line mid-flow in a 3-steps delivery with backorders, make sure that
        the OUT picking does not get packages again on its stock.move.line.
        Steps:
        - create a RX of product A for 10 units
        - on PICK_1 picking: put 2 units in Done and put in a package, validate, create a backorder
        - on PACK_1 picking: remove the destination package for the 2 units, validate, create a backorder
        - on OUT picking: the stock.move.line should not have a package
        - on PICK_2 picking: put 2 units in Done and put in a package, validate, create a backorder
        - on OUT picking: the stock.move.line should still not have a package
        - on PACK_2: validate, create a backorder
        - on OUT picking: there should be 2 stock.move.lines, one with package and one without
        """
        warehouse = self.company_data.get('default_warehouse')
        self.env['res.config.settings'].write({
            'group_stock_tracking_lot': True,
            'group_stock_adv_location': True,
            'group_stock_multi_locations': True,
        })
        warehouse.delivery_steps = 'pick_pack_ship'
        self.env['stock.quant']._update_available_quantity(self.test_product_delivery, warehouse.lot_stock_id, 10)

        rx_1 = self._get_new_prescriptions_order(product=self.test_product_delivery)
        rx_1.action_confirm()
        pick_picking = rx_1.picking_ids.filtered(lambda p: p.picking_type_id == warehouse.pick_type_id)
        pack_picking = rx_1.picking_ids.filtered(lambda p: p.picking_type_id == warehouse.pack_type_id)
        out_picking = rx_1.picking_ids.filtered(lambda p: p.picking_type_id == warehouse.out_type_id)

        pick_picking.move_ids.write({'quantity': 2, 'picked': True})
        pick_picking.action_put_in_pack()
        backorder_wizard_dict = pick_picking.button_validate()
        backorder_wizard = Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        pack_picking.move_line_ids.result_package_id = False
        pack_picking.move_ids.write({'quantity': 2, 'picked': True})
        pack_picking.button_validate()
        backorder_wizard_dict = pack_picking.button_validate()
        backorder_wizard = Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertEqual(out_picking.move_line_ids.package_id.id, False)
        self.assertEqual(out_picking.move_line_ids.result_package_id.id, False)

        pick_picking_2 = rx_1.picking_ids.filtered(lambda x: x.picking_type_id == warehouse.pick_type_id and x.state != 'sales')

        pick_picking_2.move_ids.write({'quantity': 2, 'picked': True})
        package_2 = pick_picking_2.action_put_in_pack()
        backorder_wizard_dict = pick_picking_2.button_validate()
        backorder_wizard = Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertEqual(out_picking.move_line_ids.package_id.id, False)
        self.assertEqual(out_picking.move_line_ids.result_package_id.id, False)

        pack_picking_2 = rx_1.picking_ids.filtered(lambda p: p.picking_type_id == warehouse.pack_type_id and p.state != 'sales')

        pack_picking_2.move_ids.write({'quantity': 2, 'picked': True})
        pack_picking_2.button_validate()
        backorder_wizard_dict = pack_picking_2.button_validate()
        backorder_wizard = Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process()

        self.assertRecordValues(out_picking.move_line_ids, [{'result_package_id': False}, {'result_package_id': package_2.id}])

    def test_inventory_admin_no_backorder_not_own_prescriptions_order(self):
        prescriptions_order = self._get_new_prescriptions_order()
        prescriptions_order.action_confirm()
        pick = prescriptions_order.picking_ids
        inventory_admin_user = self.env['res.users'].create({
            'name': "documents test basic user",
            'login': "dtbu",
            'email': "dtbu@yourcompany.com",
            'groups_id': [(6, 0, [
                self.ref('base.group_user'),
                self.ref('stock.group_stock_manager'),
                self.ref('pod_prescriptions_team.group_prescriptions_prescriptionsman')])]
        })
        pick.with_user(inventory_admin_user).move_ids.write(
            {'quantity': 1, 'picked': True})
        res_dict = pick.button_validate()
        wizard = Form(self.env[(res_dict.get('res_model'))].with_user(inventory_admin_user).with_context(
            res_dict['context'])).save()
        wizard.with_user(inventory_admin_user).process_cancel_backorder()

    def test_reduce_qty_ordered_no_backorder(self):
        """
        When validating a reduced picking, declining a backorder then reducing the quantity ordered on the RX line
        to match the quantity delivered, make sure that no additional picking is created.
        """

        rx_1 = self._get_new_prescriptions_order(amount=3, product=self.test_product_delivery)
        rx_1.action_confirm()
        self.assertEqual(rx_1.order_line.product_uom_qty, 3)
        self.assertEqual(len(rx_1.picking_ids), 1)

        delivery_picking = rx_1.picking_ids
        delivery_picking.move_ids.quantity = 2
        backorder_wizard_dict = delivery_picking.button_validate()
        backorder_wizard = Form(self.env[backorder_wizard_dict['res_model']].with_context(backorder_wizard_dict['context'])).save()
        backorder_wizard.process_cancel_backorder()
        self.assertEqual(rx_1.order_line.product_uom_qty, 3)
        self.assertEqual(rx_1.order_line.qty_delivered, 2)

        rx_1.write({'order_line': [(1, rx_1.order_line.id, {'product_uom_qty': rx_1.order_line.qty_delivered})]})
        self.assertEqual(len(rx_1.picking_ids), 1)

    def test_decrease_rxl_qty_to_zero(self):
        """
        2 steps delivery.
        RX with two products.
        Set the done quantity on the first picking.
        On the RX, cancel the qty of the first product:
        On the first picking, since the done quantity is already defined, it
        should only set the demand to zero. On the second picking, the SM should
        be cancelled.
        """
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        warehouse.delivery_steps = 'pick_ship'

        rx = self.env['prescriptions.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'name': p.name,
                'product_id': p.id,
                'product_uom_qty': 1,
                'product_uom': p.uom_id.id,
                'price_unit': p.list_price,
            }) for p in (
                self.product_a,
                self.product_b,
            )],
        })
        rx.action_confirm()

        pick_picking, ship_picking = rx.picking_ids
        pick_picking.move_ids.picked = True

        rx.order_line[0].product_uom_qty = 0

        self.assertRecordValues(pick_picking.move_ids, [
            {'product_id': self.product_a.id, 'product_uom_qty': 0, 'quantity': 1, 'state': 'assigned'},
            {'product_id': self.product_b.id, 'product_uom_qty': 1, 'quantity': 1, 'state': 'assigned'},
        ])
        self.assertRecordValues(ship_picking.move_ids, [
            {'product_id': self.product_a.id, 'product_uom_qty': 0, 'quantity': 0, 'state': 'cancel'},
            {'product_id': self.product_b.id, 'product_uom_qty': 1, 'quantity': 0, 'state': 'waiting'},
        ])
