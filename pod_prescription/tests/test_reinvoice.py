# -*- coding: utf-8 -*-

from freezegun import freeze_time
from odoo.addons.pod_prescription.tests.common import TestPrescriptionCommon
from odoo.tests import Form, tagged


@tagged('post_install', '-at_install')
class TestReInvoice(TestPrescriptionCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.analytic_plan = cls.env['account.analytic.plan'].create({
            'name': 'Plan',
        })

        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test AA',
            'code': 'TESTSALE_REINVOICE',
            'company_id': cls.partner_a.company_id.id,
            'plan_id': cls.analytic_plan.id,
            'partner_id': cls.partner_a.id
        })

        cls.prescription_order = cls.env['prescription.order'].with_context(mail_notrack=True, mail_create_nolog=True).create({
            'partner_id': cls.partner_a.id,
            'partner_invoice_id': cls.partner_a.id,
            'partner_shipping_id': cls.partner_a.id,
            'analytic_account_id': cls.analytic_account.id,
            'pricelist_id': cls.company_data['default_pricelist'].id,
        })

        cls.AccountMove = cls.env['account.move'].with_context(
            default_move_type='in_invoice',
            default_invoice_date=cls.prescription_order.date_order,
            mail_notrack=True,
            mail_create_nolog=True,
        )

    def test_at_cost(self):
        # Required for `analytic_account_id` to be visible in the view
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')
        """ Test vendor bill at cost for product based on ordered and delivered quantities. """
        # create RX line and confirm RX (with only one line)
        prescription_order_line1 = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_order_cost'].id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'order_id': self.prescription_order.id,
        })
        prescription_order_line2 = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_delivery_cost'].id,
            'product_uom_qty': 4,
            'qty_delivered': 1,
            'order_id': self.prescription_order.id,
        })

        self.prescription_order.action_confirm()

        # create invoice lines and validate it
        move_form = Form(self.AccountMove)
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_order_cost']
            line_form.quantity = 3.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_delivery_cost']
            line_form.quantity = 3.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        invoice_a = move_form.save()
        invoice_a.action_post()

        prescription_order_line3 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line1 and rxl.product_id == self.company_data['product_order_cost'])
        prescription_order_line4 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line2 and rxl.product_id == self.company_data['product_delivery_cost'])

        self.assertTrue(prescription_order_line3, "A new prescription line should have been created with ordered product")
        self.assertTrue(prescription_order_line4, "A new prescription line should have been created with delivered product")
        self.assertEqual(len(self.prescription_order.order_line), 4, "There should be 4 lines on the RX (2 vendor bill lines created)")
        self.assertEqual(len(self.prescription_order.order_line.filtered(lambda rxl: rxl.is_expense)), 2, "There should be 4 lines on the RX (2 vendor bill lines created)")

        self.assertEqual((prescription_order_line3.price_unit, prescription_order_line3.qty_delivered, prescription_order_line3.product_uom_qty, prescription_order_line3.qty_invoiced), (self.company_data['product_order_cost'].standard_price, 3, 0, 0), 'Prescription line is wrong after confirming vendor invoice')
        self.assertEqual((prescription_order_line4.price_unit, prescription_order_line4.qty_delivered, prescription_order_line4.product_uom_qty, prescription_order_line4.qty_invoiced), (self.company_data['product_delivery_cost'].standard_price, 3, 0, 0), 'Prescription line is wrong after confirming vendor invoice')

        self.assertEqual(prescription_order_line3.qty_delivered_method, 'analytic', "Delivered quantity of 'expense' RX line should be computed by analytic amount")
        self.assertEqual(prescription_order_line4.qty_delivered_method, 'analytic', "Delivered quantity of 'expense' RX line should be computed by analytic amount")

        # create second invoice lines and validate it
        move_form = Form(self.AccountMove)
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_order_cost']
            line_form.quantity = 2.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_delivery_cost']
            line_form.quantity = 2.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        invoice_b = move_form.save()
        invoice_b.action_post()

        prescription_order_line5 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line1 and rxl != prescription_order_line3 and rxl.product_id == self.company_data['product_order_cost'])
        prescription_order_line6 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line2 and rxl != prescription_order_line4 and rxl.product_id == self.company_data['product_delivery_cost'])

        self.assertTrue(prescription_order_line5, "A new prescription line should have been created with ordered product")
        self.assertTrue(prescription_order_line6, "A new prescription line should have been created with delivered product")

        self.assertEqual(len(self.prescription_order.order_line), 6, "There should be still 4 lines on the RX, no new created")
        self.assertEqual(len(self.prescription_order.order_line.filtered(lambda rxl: rxl.is_expense)), 4, "There should be still 2 expenses lines on the RX")

        self.assertEqual((prescription_order_line5.price_unit, prescription_order_line5.qty_delivered, prescription_order_line5.product_uom_qty, prescription_order_line5.qty_invoiced), (self.company_data['product_order_cost'].standard_price, 2, 0, 0), 'Prescription line 5 is wrong after confirming 2e vendor invoice')
        self.assertEqual((prescription_order_line6.price_unit, prescription_order_line6.qty_delivered, prescription_order_line6.product_uom_qty, prescription_order_line6.qty_invoiced), (self.company_data['product_delivery_cost'].standard_price, 2, 0, 0), 'Prescription line 6 is wrong after confirming 2e vendor invoice')

    @freeze_time('2020-01-15')
    def test_prescription_team_invoiced(self):
        """ Test invoiced field from  prescription team ony take into account the amount the prescription channel has invoiced this month """

        invoices = self.env['account.move'].create([
            {
                'move_type': 'out_invoice',
                'partner_id': self.partner_a.id,
                'invoice_date': '2020-01-10',
                'invoice_line_ids': [(0, 0, {'product_id': self.product_a.id, 'price_unit': 1000.0})],
            },
            {
                'move_type': 'out_refund',
                'partner_id': self.partner_a.id,
                'invoice_date': '2020-01-10',
                'invoice_line_ids': [(0, 0, {'product_id': self.product_a.id, 'price_unit': 500.0})],
            },
            {
                'move_type': 'in_invoice',
                'partner_id': self.partner_a.id,
                'invoice_date': '2020-01-01',
                'date': '2020-01-01',
                'invoice_line_ids': [(0, 0, {'product_id': self.product_a.id, 'price_unit': 800.0})],
            },
        ])
        invoices.action_post()

        for invoice in invoices:
            self.env['account.payment.register']\
                .with_context(active_model='account.move', active_ids=invoice.ids)\
                .create({})\
                ._create_payments()

        invoices.flush_model()
        self.assertRecordValues(invoices.team_id, [{'invoiced': 500.0}])

    def test_prescription_price(self):
        """ Test invoicing vendor bill at prescription price for products based on delivered and ordered quantities. Check no existing RX line is incremented, but when invoicing a
            second time, increment only the delivered rx line.
        """
        # Required for `analytic_account_id` to be visible in the view
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')
        # create RX line and confirm RX (with only one line)
        prescription_order_line1 = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_delivery_prescription_price'].id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'order_id': self.prescription_order.id,
        })
        prescription_order_line2 = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_order_prescription_price'].id,
            'product_uom_qty': 3,
            'qty_delivered': 1,
            'order_id': self.prescription_order.id,
        })
        self.prescription_order.action_confirm()

        # create invoice lines and validate it
        move_form = Form(self.AccountMove)
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_delivery_prescription_price']
            line_form.quantity = 3.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_order_prescription_price']
            line_form.quantity = 3.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        invoice_a = move_form.save()
        invoice_a.action_post()

        prescription_order_line3 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line1 and rxl.product_id == self.company_data['product_delivery_prescription_price'])
        prescription_order_line4 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line2 and rxl.product_id == self.company_data['product_order_prescription_price'])

        self.assertTrue(prescription_order_line3, "A new prescription line should have been created with ordered product")
        self.assertTrue(prescription_order_line4, "A new prescription line should have been created with delivered product")
        self.assertEqual(len(self.prescription_order.order_line), 4, "There should be 4 lines on the RX (2 vendor bill lines created)")
        self.assertEqual(len(self.prescription_order.order_line.filtered(lambda rxl: rxl.is_expense)), 2, "There should be 4 lines on the RX (2 vendor bill lines created)")

        self.assertEqual((prescription_order_line3.price_unit, prescription_order_line3.qty_delivered, prescription_order_line3.product_uom_qty, prescription_order_line3.qty_invoiced), (self.company_data['product_delivery_prescription_price'].list_price, 3, 0, 0), 'Prescription line is wrong after confirming vendor invoice')
        self.assertEqual((prescription_order_line4.price_unit, prescription_order_line4.qty_delivered, prescription_order_line4.product_uom_qty, prescription_order_line4.qty_invoiced), (self.company_data['product_order_prescription_price'].list_price, 3, 0, 0), 'Prescription line is wrong after confirming vendor invoice')

        self.assertEqual(prescription_order_line3.qty_delivered_method, 'analytic', "Delivered quantity of 'expense' RX line 3 should be computed by analytic amount")
        self.assertEqual(prescription_order_line4.qty_delivered_method, 'analytic', "Delivered quantity of 'expense' RX line 4 should be computed by analytic amount")

        # create second invoice lines and validate it
        move_form = Form(self.AccountMove)
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_delivery_prescription_price']
            line_form.quantity = 2.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_order_prescription_price']
            line_form.quantity = 2.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        invoice_b = move_form.save()
        invoice_b.action_post()

        prescription_order_line5 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line1 and rxl != prescription_order_line3 and rxl.product_id == self.company_data['product_delivery_prescription_price'])
        prescription_order_line6 = self.prescription_order.order_line.filtered(lambda rxl: rxl != prescription_order_line2 and rxl != prescription_order_line4 and rxl.product_id == self.company_data['product_order_prescription_price'])

        self.assertFalse(prescription_order_line5, "No new prescription line should have been created with delivered product !!")
        self.assertTrue(prescription_order_line6, "A new prescription line should have been created with ordered product")

        self.assertEqual(len(self.prescription_order.order_line), 5, "There should be 5 lines on the RX, 1 new created and 1 incremented")
        self.assertEqual(len(self.prescription_order.order_line.filtered(lambda rxl: rxl.is_expense)), 3, "There should be 3 expenses lines on the RX")

        self.assertEqual((prescription_order_line6.price_unit, prescription_order_line6.qty_delivered, prescription_order_line4.product_uom_qty, prescription_order_line6.qty_invoiced), (self.company_data['product_order_prescription_price'].list_price, 2, 0, 0), 'Prescription line is wrong after confirming 2e vendor invoice')

    def test_no_expense(self):
        """ Test invoicing vendor bill with no policy. Check nothing happen. """
        # Required for `analytic_account_id` to be visible in the view
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')
        # confirm RX
        prescription_order_line = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_delivery_no'].id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'order_id': self.prescription_order.id,
        })
        self.prescription_order.action_confirm()

        # create invoice lines and validate it
        move_form = Form(self.AccountMove)
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.company_data['product_delivery_no']
            line_form.quantity = 3.0
            line_form.analytic_distribution = {self.analytic_account.id: 100}
        invoice_a = move_form.save()
        invoice_a.action_post()

        self.assertEqual(len(self.prescription_order.order_line), 1, "No RX line should have been created (or removed) when validating vendor bill")
        self.assertTrue(invoice_a.mapped('line_ids.analytic_line_ids'), "Analytic lines should be generated")

    def test_not_reinvoicing_invoiced_rx_lines(self):
        """ Test that invoiced RX lines are not re-invoiced. """
        rx_line1 = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_delivery_cost'].id,
            'discount': 100.00,
            'order_id': self.prescription_order.id,
        })
        rx_line2 = self.env['prescription.order.line'].create({
            'product_id': self.company_data['product_delivery_prescription_price'].id,
            'discount': 100.00,
            'order_id': self.prescription_order.id,
        })

        self.prescription_order.action_confirm()

        for line in self.prescription_order.order_line:
            line.qty_delivered = 1
        # create invoice and validate it
        invoice = self.prescription_order._create_invoices()
        invoice.action_post()

        rx_line3 = self.prescription_order.order_line.filtered(lambda rxl: rxl != rx_line1 and rxl.product_id == self.company_data['product_delivery_cost'])
        rx_line4 = self.prescription_order.order_line.filtered(lambda rxl: rxl != rx_line2 and rxl.product_id == self.company_data['product_delivery_prescription_price'])

        self.assertFalse(rx_line3, "No re-invoicing should have created a new prescription line with product #1")
        self.assertFalse(rx_line4, "No re-invoicing should have created a new prescription line with product #2")
        self.assertEqual(rx_line1.qty_delivered, 1, "No re-invoicing should have impacted exising RX line 1")
        self.assertEqual(rx_line2.qty_delivered, 1, "No re-invoicing should have impacted exising RX line 2")
