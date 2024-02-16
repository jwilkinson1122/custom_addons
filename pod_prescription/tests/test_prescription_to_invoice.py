# -*- coding: utf-8 -*-


from odoo import fields
from odoo.fields import Command
from odoo.tests import Form, tagged
from odoo.tools import float_is_zero

from odoo.addons.pod_prescription.tests.common import TestPrescriptionCommon


@tagged('-at_install', 'post_install')
class TestPrescriptionToInvoice(TestPrescriptionCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # Create the RX with four order lines
        cls.prescription_order = cls.env['prescription.order'].with_context(tracking_disable=True).create({
            'partner_id': cls.partner_a.id,
            'partner_invoice_id': cls.partner_a.id,
            'partner_shipping_id': cls.partner_a.id,
            'pricelist_id': cls.company_data['default_pricelist'].id,
            'order_line': [
                Command.create({
                    'product_id': cls.company_data['product_order_no'].id,
                    'product_uom_qty': 5,
                    'tax_id': False,
                }),
                Command.create({
                    'product_id': cls.company_data['product_service_delivery'].id,
                    'product_uom_qty': 4,
                    'tax_id': False,
                }),
                Command.create({
                    'product_id': cls.company_data['product_service_order'].id,
                    'product_uom_qty': 3,
                    'tax_id': False,
                }),
                Command.create({
                    'product_id': cls.company_data['product_delivery_no'].id,
                    'product_uom_qty': 2,
                    'tax_id': False,
                }),
            ]
        })

        (
            cls.rxl_prod_order,
            cls.rxl_serv_deliver,
            cls.rxl_serv_order,
            cls.rxl_prod_deliver,
        ) = cls.prescription_order.order_line

        # Context
        cls.context = {
            'active_model': 'prescription.order',
            'active_ids': [cls.prescription_order.id],
            'active_id': cls.prescription_order.id,
            'default_journal_id': cls.company_data['default_journal_prescription'].id,
        }

    def _check_order_search(self, orders, domain, expected_result):
        domain += [('id', 'in', orders.ids)]
        result = self.env['prescription.order'].search(domain)
        self.assertEqual(result, expected_result, "Unexpected result on search orders")

    def test_search_invoice_ids(self):
        """Test searching on computed fields invoice_ids"""

        # Make qty zero to have a line without invoices
        self.rxl_prod_order.product_uom_qty = 0
        self.prescription_order.action_confirm()

        # Tests before creating an invoice
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.prescription_order)
        self._check_order_search(self.prescription_order, [('invoice_ids', '!=', False)], self.env['prescription.order'])

        # Create invoice
        moves = self.prescription_order._create_invoices()

        # Tests after creating the invoice
        self._check_order_search(self.prescription_order, [('invoice_ids', 'in', moves.ids)], self.prescription_order)
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.env['prescription.order'])
        self._check_order_search(self.prescription_order, [('invoice_ids', '!=', False)], self.prescription_order)

    def test_downpayment(self):
        """ Test invoice with a way of downpayment and check downpayment's RX line is created
            and also check a total amount of invoice is equal to a respective prescription order's total amount
        """
        # Confirm the RX
        self.prescription_order.action_confirm()
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.prescription_order)
        # Let's do an invoice for a deposit of 100
        downpayment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'fixed',
            'fixed_amount': 50,
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        downpayment2 = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'fixed',
            'fixed_amount': 50,
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        downpayment2.create_invoices()
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.env['prescription.order'])

        self.assertEqual(len(self.prescription_order.invoice_ids), 2, 'Invoice should be created for the RX')
        downpayment_line = self.prescription_order.order_line.filtered(lambda l: l.is_downpayment and not l.display_type)
        self.assertEqual(len(downpayment_line), 2, 'RX line downpayment should be created on RX')

        # Update delivered quantity of RX lines
        self.rxl_serv_deliver.write({'qty_delivered': 4.0})
        self.rxl_prod_deliver.write({'qty_delivered': 2.0})

        # Let's do an invoice with refunds
        payment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        payment.create_invoices()

        self.assertEqual(len(self.prescription_order.invoice_ids), 3, 'Invoice should be created for the RX')

        invoice = max(self.prescription_order.invoice_ids)
        self.assertEqual(len(invoice.invoice_line_ids.filtered(lambda l: not (l.display_type == 'line_section' and l.name == "Down Payments"))),
                         len(self.prescription_order.order_line.filtered(lambda l: not (l.display_type == 'line_section' and l.name == "Down Payments"))), 'All lines should be invoiced')
        self.assertEqual(len(invoice.invoice_line_ids.filtered(lambda l: l.display_type == 'line_section' and l.name == "Down Payments")), 1, 'A single section for downpayments should be present')
        self.assertEqual(invoice.amount_total, self.prescription_order.amount_total - sum(downpayment_line.mapped('price_unit')), 'Downpayment should be applied')

    def test_downpayment_validation(self):
        """ Test invoice for downpayment and check it can be validated
        """
        # Lock the prescription orders when confirmed
        self.env.user.groups_id += self.env.ref('pod_prescription.group_auto_done_setting')

        # Confirm the RX
        self.prescription_order.action_confirm()
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.prescription_order)
        # Let's do an invoice for a deposit of 10%
        downpayment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'percentage',
            'amount': 10,
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.env['prescription.order'])

        # Update delivered quantity of RX lines
        self.rxl_serv_deliver.write({'qty_delivered': 4.0})
        self.rxl_prod_deliver.write({'qty_delivered': 2.0})

        # Validate invoice
        self.prescription_order.invoice_ids.action_post()

    def test_downpayment_line_remains_on_RX(self):
        """ Test downpayment's RX line is created and remains unchanged even if everything is invoiced
        """
        # Create the RX with one line
        prescription_order = self.env['prescription.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'pricelist_id': self.company_data['default_pricelist'].id,
            'order_line': [Command.create({
                'product_id': self.company_data['product_order_no'].id,
                'product_uom_qty': 5,
                'tax_id': False,
            }),]
        })
        # Confirm the RX
        prescription_order.action_confirm()
        # Update delivered quantity of RX line
        prescription_order.order_line.write({'qty_delivered': 5.0})
        context = {
            'active_model': 'prescription.order',
            'active_ids': [prescription_order.id],
            'active_id': prescription_order.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }
        # Let's do an invoice for a down payment of 50
        downpayment = self.env['prescription.advance.payment.inv'].with_context(context).create({
            'advance_payment_method': 'fixed',
            'fixed_amount': 50,
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        # Let's do the invoice
        payment = self.env['prescription.advance.payment.inv'].with_context(context).create({
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        payment.create_invoices()
        # Confirm all invoices
        for invoice in prescription_order.invoice_ids:
            invoice.action_post()
        downpayment_line = prescription_order.order_line.filtered(lambda l: l.is_downpayment and not l.display_type)
        self.assertEqual(downpayment_line[0].price_unit, 50, 'The down payment unit price should not change on RX')

    def test_downpayment_fixed_amount_with_zero_total_amount(self):
        # Create the RX with one line and amount total is zero
        prescription_order = self.env['prescription.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'pricelist_id': self.company_data['default_pricelist'].id,
            'order_line': [Command.create({
                'product_id': self.company_data['product_order_no'].id,
                'product_uom_qty': 5,
                'price_unit': 0,
                'tax_id': False,
            }), ]
        })
        prescription_order.action_confirm()
        prescription_order.order_line.write({'qty_delivered': 5.0})
        context = {
            'active_model': 'prescription.order',
            'active_ids': [prescription_order.id],
            'active_id': prescription_order.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }
        # Let's do an invoice for a down payment of 50
        downpayment = self.env['prescription.advance.payment.inv'].with_context(context).create({
            'advance_payment_method': 'fixed',
            'fixed_amount': 50,
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        # Create invoice
        downpayment.create_invoices()
        self.assertEqual(downpayment.amount, 0.0, 'The down payment amount should be 0.0')

    def test_downpayment_percentage_tax_icl(self):
        """ Test invoice with a percentage downpayment and an included tax
            Check the total amount of invoice is correct and equal to a respective prescription order's total amount
        """
        # Confirm the RX
        self.prescription_order.action_confirm()
        tax_downpayment = self.company_data['default_tax_prescription'].copy({
            'name': 'default price included',
            'price_include': True,
        })
        # Let's do an invoice for a deposit of 100
        product_id = self.env.company.prescription_down_payment_product_id
        product_id.taxes_id = tax_downpayment.ids
        payment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'percentage',
            'amount': 50,
            'deposit_account_id': self.company_data['default_account_revenue'].id,
        })
        payment.create_invoices()

        self.assertEqual(len(self.prescription_order.invoice_ids), 1, 'Invoice should be created for the RX')
        downpayment_line = self.prescription_order.order_line.filtered(lambda l: l.is_downpayment and not l.display_type)
        self.assertEqual(len(downpayment_line), 1, 'RX line downpayment should be created on RX')
        self.assertEqual(downpayment_line.price_unit, self.prescription_order.amount_total/2, 'downpayment should have the correct amount')

        invoice = self.prescription_order.invoice_ids[0]
        downpayment_aml = invoice.line_ids.filtered(lambda l: not (l.display_type == 'line_section' and l.name == "Down Payments"))[0]
        self.assertEqual(downpayment_aml.price_total, self.prescription_order.amount_total/2, 'downpayment should have the correct amount')
        self.assertEqual(downpayment_aml.price_unit, self.prescription_order.amount_total/2, 'downpayment should have the correct amount')
        invoice.action_post()
        self.assertEqual(downpayment_line.price_unit, self.prescription_order.amount_total/2, 'downpayment should have the correct amount')

    def test_invoice_with_discount(self):
        """ Test invoice with a discount and check discount applied on both RX lines and an invoice lines """
        # Update discount and delivered quantity on RX lines
        self.rxl_prod_order.write({'discount': 20.0})
        self.rxl_serv_deliver.write({'discount': 20.0, 'qty_delivered': 4.0})
        self.rxl_serv_order.write({'discount': -10.0})
        self.rxl_prod_deliver.write({'qty_delivered': 2.0})

        for line in self.prescription_order.order_line.filtered(lambda l: l.discount):
            product_price = line.price_unit * line.product_uom_qty
            self.assertEqual(line.discount, (product_price - line.price_subtotal) / product_price * 100, 'Discount should be applied on order line')

        # lines are in draft
        for line in self.prescription_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_to_invoice, precision_digits=2), "The amount to invoice should be zero, as the line is in draf state")
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced, precision_digits=2), "The invoiced amount should be zero, as the line is in draft state")

        self.prescription_order.action_confirm()

        for line in self.prescription_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced, precision_digits=2), "The invoiced amount should be zero, as the line is in draft state")

        self.assertEqual(
            self.rxl_serv_order.untaxed_amount_to_invoice,
            297,
            "The untaxed amount to invoice is wrong")
        self.assertEqual(
            self.rxl_serv_deliver.untaxed_amount_to_invoice,
            576,
            "The untaxed amount to invoice should be qty deli * price reduce, rx 4 * (180 - 36)")
        # 'untaxed_amount_to_invoice' is invalid when 'pod_prescription_stock' is installed.
        # self.assertEqual(self.rxl_prod_deliver.untaxed_amount_to_invoice, 140, "The untaxed amount to invoice should be qty deli * price reduce, rx 4 * (180 - 36)")

        # Let's do an invoice with invoiceable lines
        payment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'delivered'
        })
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.prescription_order)
        payment.create_invoices()
        self._check_order_search(self.prescription_order, [('invoice_ids', '=', False)], self.env['prescription.order'])
        invoice = self.prescription_order.invoice_ids[0]
        invoice.action_post()

        # Check discount appeared on both RX lines and invoice lines
        for line, inv_line in zip(self.prescription_order.order_line, invoice.invoice_line_ids):
            self.assertEqual(line.discount, inv_line.discount, 'Discount on lines of order and invoice should be same')

    def test_invoice(self):
        """ Test create and invoice from the RX, and check qty invoice/to invoice, and the related amounts """
        # lines are in draft
        for line in self.prescription_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_to_invoice, precision_digits=2), "The amount to invoice should be zero, as the line is in draf state")
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced, precision_digits=2), "The invoiced amount should be zero, as the line is in draft state")

        # Confirm the RX
        self.prescription_order.action_confirm()

        # Check ordered quantity, quantity to invoice and invoiced quantity of RX lines
        for line in self.prescription_order.order_line:
            if line.product_id.invoice_policy == 'delivery':
                self.assertEqual(line.qty_to_invoice, 0.0, 'Quantity to invoice should be same as ordered quantity')
                self.assertEqual(line.qty_invoiced, 0.0, 'Invoiced quantity should be zero as no any invoice created for RX')
                self.assertEqual(line.untaxed_amount_to_invoice, 0.0, "The amount to invoice should be zero, as the line based on delivered quantity")
                self.assertEqual(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as the line based on delivered quantity")
            else:
                self.assertEqual(line.qty_to_invoice, line.product_uom_qty, 'Quantity to invoice should be same as ordered quantity')
                self.assertEqual(line.qty_invoiced, 0.0, 'Invoiced quantity should be zero as no any invoice created for RX')
                self.assertEqual(line.untaxed_amount_to_invoice, line.product_uom_qty * line.price_unit, "The amount to invoice should the total of the line, as the line is confirmed")
                self.assertEqual(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as the line is confirmed")

        # Let's do an invoice with invoiceable lines
        payment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'delivered'
        })
        payment.create_invoices()

        invoice = self.prescription_order.invoice_ids[0]

        # Update quantity of an invoice lines
        move_form = Form(invoice)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.quantity = 3.0
        with move_form.invoice_line_ids.edit(1) as line_form:
            line_form.quantity = 2.0
        invoice = move_form.save()

        # amount to invoice / invoiced should not have changed (amounts take only confirmed invoice into account)
        for line in self.prescription_order.order_line:
            if line.product_id.invoice_policy == 'delivery':
                self.assertEqual(line.qty_to_invoice, 0.0, "Quantity to invoice should be zero")
                self.assertEqual(line.qty_invoiced, 0.0, "Invoiced quantity should be zero as delivered lines are not delivered yet")
                self.assertEqual(line.untaxed_amount_to_invoice, 0.0, "The amount to invoice should be zero, as the line based on delivered quantity (no confirmed invoice)")
                self.assertEqual(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as no invoice are validated for now")
            else:
                if line == self.rxl_prod_order:
                    self.assertEqual(self.rxl_prod_order.qty_to_invoice, 2.0, "Changing the quantity on draft invoice update the qty to invoice on RX lines")
                    self.assertEqual(self.rxl_prod_order.qty_invoiced, 3.0, "Changing the quantity on draft invoice update the invoiced qty on RX lines")
                else:
                    self.assertEqual(self.rxl_serv_order.qty_to_invoice, 1.0, "Changing the quantity on draft invoice update the qty to invoice on RX lines")
                    self.assertEqual(self.rxl_serv_order.qty_invoiced, 2.0, "Changing the quantity on draft invoice update the invoiced qty on RX lines")
                self.assertEqual(line.untaxed_amount_to_invoice, line.product_uom_qty * line.price_unit, "The amount to invoice should the total of the line, as the line is confirmed (no confirmed invoice)")
                self.assertEqual(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as no invoice are validated for now")

        invoice.action_post()

        # Check quantity to invoice on RX lines
        for line in self.prescription_order.order_line:
            if line.product_id.invoice_policy == 'delivery':
                self.assertEqual(line.qty_to_invoice, 0.0, "Quantity to invoice should be same as ordered quantity")
                self.assertEqual(line.qty_invoiced, 0.0, "Invoiced quantity should be zero as no any invoice created for RX")
                self.assertEqual(line.untaxed_amount_to_invoice, 0.0, "The amount to invoice should be zero, as the line based on delivered quantity")
                self.assertEqual(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as the line based on delivered quantity")
            else:
                if line == self.rxl_prod_order:
                    self.assertEqual(line.qty_to_invoice, 2.0, "The ordered prescription line are totally invoiced (qty to invoice is zero)")
                    self.assertEqual(line.qty_invoiced, 3.0, "The ordered (prod) prescription line are totally invoiced (qty invoiced come from the invoice lines)")
                else:
                    self.assertEqual(line.qty_to_invoice, 1.0, "The ordered prescription line are totally invoiced (qty to invoice is zero)")
                    self.assertEqual(line.qty_invoiced, 2.0, "The ordered (serv) prescription line are totally invoiced (qty invoiced = the invoice lines)")
                self.assertEqual(line.untaxed_amount_to_invoice, line.price_unit * line.qty_to_invoice, "Amount to invoice is now set as qty to invoice * unit price since no price change on invoice, for ordered products")
                self.assertEqual(line.untaxed_amount_invoiced, line.price_unit * line.qty_invoiced, "Amount invoiced is now set as qty invoiced * unit price since no price change on invoice, for ordered products")

    def test_multiple_prescription_orders_on_same_invoice(self):
        """ The model allows the association of multiple RX lines linked to the same invoice line.
            Check that the operations behave well, if a custom module creates such a situation.
        """
        self.prescription_order.action_confirm()
        payment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'delivered'
        })
        payment.create_invoices()

        # create a second RX whose lines are linked to the same invoice lines
        # this is a way to create a situation where prescription_line_ids has multiple items
        prescription_order_data = self.prescription_order.copy_data()[0]
        prescription_order_data['order_line'] = [
            (0, 0, line.copy_data({
                'invoice_lines': [(6, 0, line.invoice_lines.ids)],
            })[0])
            for line in self.prescription_order.order_line
        ]
        self.prescription_order.create(prescription_order_data)

        # we should now have at least one move line linked to several order lines
        invoice = self.prescription_order.invoice_ids[0]
        self.assertTrue(any(len(move_line.prescription_line_ids) > 1
                            for move_line in invoice.line_ids))

        # however these actions should not raise
        invoice.action_post()
        invoice.button_draft()
        invoice.button_cancel()

    def test_invoice_with_sections(self):
        """ Test create and invoice with sections from the RX, and check qty invoice/to invoice, and the related amounts """

        prescription_order = self.env['prescription.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'pricelist_id': self.company_data['default_pricelist'].id,
        })

        PrescriptionOrderLine = self.env['prescription.order.line'].with_context(tracking_disable=True)
        PrescriptionOrderLine.create({
            'name': 'Section',
            'display_type': 'line_section',
            'order_id': prescription_order.id,
        })
        rxl_prod_deliver = PrescriptionOrderLine.create({
            'product_id': self.company_data['product_order_no'].id,
            'product_uom_qty': 5,
            'order_id': prescription_order.id,
            'tax_id': False,
        })

        # Confirm the RX
        prescription_order.action_confirm()

        rxl_prod_deliver.write({'qty_delivered': 5.0})

        # Context
        self.context = {
            'active_model': 'prescription.order',
            'active_ids': [prescription_order.id],
            'active_id': prescription_order.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }

        # Let's do an invoice with invoiceable lines
        payment = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'delivered'
        })
        payment.create_invoices()

        invoice = prescription_order.invoice_ids[0]

        self.assertEqual(invoice.line_ids[0].display_type, 'line_section')

    def test_qty_invoiced(self):
        """Verify uom rounding is correctly considered during qty_invoiced compute"""
        prescription_order = self.env['prescription.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'pricelist_id': self.company_data['default_pricelist'].id,
        })

        PrescriptionOrderLine = self.env['prescription.order.line'].with_context(tracking_disable=True)
        rxl_prod_deliver = PrescriptionOrderLine.create({
            'product_id': self.company_data['product_order_no'].id,
            'product_uom_qty': 5,
            'order_id': prescription_order.id,
            'tax_id': False,
        })

        # Confirm the RX
        prescription_order.action_confirm()

        rxl_prod_deliver.write({'qty_delivered': 5.0})
        # Context
        self.context = {
            'active_model': 'prescription.order',
            'active_ids': [prescription_order.id],
            'active_id': prescription_order.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }

        # Let's do an invoice with invoiceable lines
        invoicing_wizard = self.env['prescription.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'delivered'
        })
        invoicing_wizard.create_invoices()

        self.assertEqual(rxl_prod_deliver.qty_invoiced, 5.0)
        # We would have to change the digits of the field to
        # test a greater decimal precision.
        quantity = 5.13
        move_form = Form(prescription_order.invoice_ids)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.quantity = quantity
        move_form.save()

        # Default uom rounding to 0.01
        qty_invoiced_field = rxl_prod_deliver._fields.get('qty_invoiced')
        rxl_prod_deliver.env.add_to_compute(qty_invoiced_field, rxl_prod_deliver)
        self.assertEqual(rxl_prod_deliver.qty_invoiced, quantity)

        # Rounding to 0.1, should be rounded with UP (ceil) rounding_method
        # Not floor or half up rounding.
        rxl_prod_deliver.product_uom.rounding *= 10
        rxl_prod_deliver.product_uom.flush_recordset(['rounding'])
        expected_qty = 5.2
        qty_invoiced_field = rxl_prod_deliver._fields.get('qty_invoiced')
        rxl_prod_deliver.env.add_to_compute(qty_invoiced_field, rxl_prod_deliver)
        self.assertEqual(rxl_prod_deliver.qty_invoiced, expected_qty)

    def test_multi_company_invoice(self):
        """Checks that the company of the invoices generated in a multi company environment using the
           'prescription.advance.payment.inv' wizard fit with the company of the RX and not with the current company.
        """
        rx_company_id = self.prescription_order.company_id.id
        yet_another_company_id = self.company_data_2['company'].id
        rx_for_downpayment = self.prescription_order.copy()

        self.context.update(allowed_company_ids=[yet_another_company_id, self.env.company.id], company_id=yet_another_company_id)
        context_for_downpayment = self.context.copy()
        context_for_downpayment.update(active_ids=[rx_for_downpayment.id], active_id=rx_for_downpayment.id)

        # Make sure the invoice is not created with a journal in the context
        # Because it makes the test always succeed (by using the journal company instead of the env company)
        no_journal_ctxt = dict(self.context)
        no_journal_ctxt.pop('default_journal_id', None)
        no_journal_ctxt.pop('journal_id', None)

        self.prescription_order.with_context(self.context).action_confirm()
        payment = self.env['prescription.advance.payment.inv'].with_context(no_journal_ctxt).create({
            'advance_payment_method': 'percentage',
            'amount': 50,
        })
        payment.create_invoices()
        self.assertEqual(self.prescription_order.invoice_ids[0].company_id.id, rx_company_id, "The company of the invoice should be the same as the one from the RX")

        rx_for_downpayment.with_context(context_for_downpayment).action_confirm()
        downpayment = self.env['prescription.advance.payment.inv'].with_context(context_for_downpayment).create({
            'advance_payment_method': 'fixed',
            'fixed_amount': 50,
            'deposit_account_id': self.company_data['default_account_revenue'].id
        })
        downpayment.create_invoices()
        self.assertEqual(rx_for_downpayment.invoice_ids[0].company_id.id, rx_company_id, "The company of the downpayment invoice should be the same as the one from the RX")

    def test_invoice_analytic_distribution_model(self):
        """ Tests whether, when an analytic account rule is set and the rx has no analytic account,
        the default analytic account is correctly computed in the invoice.
        """
        analytic_plan_default = self.env['account.analytic.plan'].create({'name': 'default'})
        analytic_account_default = self.env['account.analytic.account'].create({'name': 'default', 'plan_id': analytic_plan_default.id})

        self.env['account.analytic.distribution.model'].create({
            'analytic_distribution': {analytic_account_default.id: 100},
            'product_id': self.product_a.id,
        })

        rx_form = Form(self.env['prescription.order'])
        rx_form.partner_id = self.partner_a

        with rx_form.order_line.new() as rxl:
            rxl.product_id = self.product_a
            rxl.product_uom_qty = 1

        rx = rx_form.save()
        rx.action_confirm()
        rx._force_lines_to_invoice_policy_order()

        rx_context = {
            'active_model': 'prescription.order',
            'active_ids': [rx.id],
            'active_id': rx.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }
        down_payment = self.env['prescription.advance.payment.inv'].with_context(rx_context).create({})
        down_payment.create_invoices()

        aml = self.env['account.move.line'].search([('move_id', 'in', rx.invoice_ids.ids)])[0]
        self.assertRecordValues(aml, [{'analytic_distribution': {str(analytic_account_default.id): 100}}])

    def test_invoice_analytic_account_rx_not_default(self):
        """ Tests whether, when an analytic account rule is set and the rx has an analytic account,
        the default analytic acount doesn't replace the one from the rx in the invoice.
        """
        # Required for `analytic_account_id` to be visible in the view
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')
        analytic_plan_default = self.env['account.analytic.plan'].create({'name': 'default'})
        analytic_account_default = self.env['account.analytic.account'].create({'name': 'default', 'plan_id': analytic_plan_default.id})
        analytic_account_rx = self.env['account.analytic.account'].create({'name': 'rx', 'plan_id': analytic_plan_default.id})

        self.env['account.analytic.distribution.model'].create({
            'analytic_distribution': {analytic_account_default.id: 100},
            'product_id': self.product_a.id,
        })

        rx_form = Form(self.env['prescription.order'])
        rx_form.partner_id = self.partner_a
        rx_form.analytic_account_id = analytic_account_rx

        with rx_form.order_line.new() as rxl:
            rxl.product_id = self.product_a
            rxl.product_uom_qty = 1

        rx = rx_form.save()
        rx.action_confirm()
        rx._force_lines_to_invoice_policy_order()

        rx_context = {
            'active_model': 'prescription.order',
            'active_ids': [rx.id],
            'active_id': rx.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }
        down_payment = self.env['prescription.advance.payment.inv'].with_context(rx_context).create({})
        down_payment.create_invoices()

        aml = self.env['account.move.line'].search([('move_id', 'in', rx.invoice_ids.ids)])[0]
        self.assertRecordValues(aml, [{'analytic_distribution': {str(analytic_account_default.id): 100, str(analytic_account_rx.id): 100}}])

    def test_invoice_analytic_rule_with_account_prefix(self):
        """
        Test whether, when an analytic account rule is set within the scope (applicability) of invoice
        and with an account prefix set,
        the default analytic account is correctly set during the conversion from rx to invoice
        """
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')
        analytic_plan_default = self.env['account.analytic.plan'].create({
            'name': 'default',
            'applicability_ids': [Command.create({
                'business_domain': 'invoice',
                'applicability': 'optional',
            })]
        })
        analytic_account_default = self.env['account.analytic.account'].create({'name': 'default', 'plan_id': analytic_plan_default.id})

        analytic_distribution_model = self.env['account.analytic.distribution.model'].create({
            'account_prefix': '400000',
            'analytic_distribution': {analytic_account_default.id: 100},
            'product_id': self.product_a.id,
        })

        rx = self.env['prescription.order'].create({'partner_id': self.partner_a.id})
        self.env['prescription.order.line'].create({
            'order_id': rx.id,
            'name': 'test',
            'product_id': self.product_a.id
        })
        self.assertFalse(rx.order_line.analytic_distribution, "There should be no tag set.")
        rx.action_confirm()
        rx.order_line.qty_delivered = 1
        aml = rx._create_invoices().invoice_line_ids
        self.assertRecordValues(aml, [{'analytic_distribution': analytic_distribution_model.analytic_distribution}])

    def test_invoice_after_product_return_price_not_default(self):
        rx = self.env['prescription.order'].create({
            'name': 'Prescription order',
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'order_line': [
                (0, 0, {'name': self.product_a.name, 'product_id': self.product_a.id, 'product_uom_qty': 1, 'price_unit': 123}),
            ]
        })
        self._check_order_search(rx, [('invoice_ids', '=', False)], rx)
        rx.action_confirm()
        rx_context = {
            'active_model': 'prescription.order',
            'active_ids': [rx.id],
            'active_id': rx.id,
            'default_journal_id': self.company_data['default_journal_prescription'].id,
        }
        invoicing_wizard = self.env['prescription.advance.payment.inv'].with_context(rx_context).create({})
        invoicing_wizard.create_invoices()
        self.assertTrue(rx.invoice_ids, "The invoice was not created")
        # simulating return by changing product_uom_qty to 0
        rx.order_line.product_uom_qty = 0
        # checking if the price_unit is the same
        self.assertEqual(rx.order_line.price_unit, 123,
                         "The unit price should be the same as the one used to create the prescription order line")

    def test_group_invoice(self):
        """ Test that invoicing multiple prescription order for the same customer works. """
        # Create 3 RXs for the same partner, one of which that uses another currency
        eur_pricelist = self.env['product.pricelist'].create({'name': 'EUR', 'currency_id': self.env.ref('base.EUR').id})
        rx1 = self.prescription_order.with_context(mail_notrack=True).copy()
        rx1.pricelist_id = eur_pricelist
        rx2 = rx1.copy()
        usd_pricelist = self.env['product.pricelist'].create({'name': 'USD', 'currency_id': self.env.ref('base.USD').id})
        rx3 = rx1.copy()
        rx1.pricelist_id = usd_pricelist
        orders = rx1 | rx2 | rx3
        orders.action_confirm()
        # Create the invoicing wizard and invoice all of them at once
        wiz = self.env['prescription.advance.payment.inv'].with_context(active_ids=orders.ids, open_invoices=True).create({})
        res = wiz.create_invoices()
        # Check that exactly 2 invoices are generated
        self.assertEqual(
            len(res['domain'][0][2]),
            2,
            "Invoicing 3 orders for the same partner with 2 currencies"
            "should create exactly 2 invoices.")

    def test_rx_note_to_invoice(self):
        """Test that notes from RX are pushed into invoices"""

        self.prescription_order.order_line = [Command.create({
            'name': 'This is a note',
            'display_type': 'line_note',
            'product_id': False,
            'product_uom_qty': 0,
            'product_uom': False,
            'price_unit': 0,
            'order_id': self.prescription_order.id,
            'tax_id': False,
        })]

        # confirm quotation
        self.prescription_order.action_confirm()

        # create invoice
        invoice = self.prescription_order._create_invoices()

        # check note from RX has been pushed in invoice
        self.assertEqual(
            len(invoice.invoice_line_ids.filtered(lambda line: line.display_type == 'line_note')),
            1,
            'Note RX line should have been pushed to the invoice')

    def test_cost_invoicing(self):
        """ Test confirming a vendor invoice to reinvoice cost on the rx """
        serv_cost = self.env['product.product'].create({
            'name': "Ordered at cost",
            'standard_price': 160,
            'list_price': 180,
            'type': 'consu',
            'invoice_policy': 'order',
            'expense_policy': 'cost',
            'default_code': 'PROD_COST',
            'service_type': 'manual',
        })
        prod_gap = self.company_data['product_service_order']
        rx = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'partner_invoice_id': self.partner_a.id,
            'partner_shipping_id': self.partner_a.id,
            'order_line': [Command.create({
                'product_id': prod_gap.id,
                'product_uom_qty': 2,
                'product_uom': prod_gap.uom_id.id,
                'price_unit': prod_gap.list_price,
            })],
            'pricelist_id': self.company_data['default_pricelist'].id,
        })
        rx.action_confirm()
        rx._create_analytic_account()

        inv = self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'partner_id': self.partner_a.id,
            'invoice_date': rx.date_order,
            'invoice_line_ids': [
                Command.create({
                    'name': serv_cost.name,
                    'product_id': serv_cost.id,
                    'product_uom_id': serv_cost.uom_id.id,
                    'quantity': 2,
                    'price_unit': serv_cost.standard_price,
                    'analytic_distribution': {rx.analytic_account_id.id: 100},
                }),
            ],
        })
        inv.action_post()
        rxl = rx.order_line.filtered(lambda l: l.product_id == serv_cost)
        self.assertTrue(rxl, 'Prescription: cost invoicing does not add lines when confirming vendor invoice')
        self.assertEqual(
            (rxl.price_unit, rxl.qty_delivered, rxl.product_uom_qty, rxl.qty_invoiced),
            (160, 2, 0, 0),
            'Prescription: line is wrong after confirming vendor invoice')

    def test_prescription_order_standard_flow_with_invoicing(self):
        """ Test the prescription order flow (invoicing and quantity updates)
            - Invoice repeatedly while varrying delivered quantities and check that invoice are always what we expect
        """
        self.prescription_order.order_line.product_uom_qty = 2.0
        # TODO?: validate invoice and register payments
        self.prescription_order.order_line.read(['name', 'price_unit', 'product_uom_qty', 'price_total'])

        self.assertEqual(self.prescription_order.amount_total, 1240.0, 'Prescription: total amount is wrong')
        self.prescription_order.order_line._compute_product_updatable()
        self.assertTrue(self.prescription_order.order_line[0].product_updatable)
        # send quotation
        email_act = self.prescription_order.action_quotation_send()
        email_ctx = email_act.get('context', {})
        self.prescription_order.with_context(**email_ctx).message_post_with_source(
            self.env['mail.template'].browse(email_ctx.get('default_template_id')),
            subtype_xmlid='mail.mt_comment',
        )
        self.assertTrue(self.prescription_order.state == 'sent', 'Prescription: state after sending is wrong')
        self.prescription_order.order_line._compute_product_updatable()
        self.assertTrue(self.prescription_order.order_line[0].product_updatable)

        # confirm quotation
        self.prescription_order.action_confirm()
        self.assertTrue(self.prescription_order.state == 'prescription')
        self.assertTrue(self.prescription_order.invoice_status == 'to invoice')

        # create invoice: only 'invoice on order' products are invoiced
        invoice = self.prescription_order._create_invoices()
        self.assertEqual(len(invoice.invoice_line_ids), 2, 'Prescription: invoice is missing lines')
        self.assertEqual(invoice.amount_total, 740.0, 'Prescription: invoice total amount is wrong')
        self.assertTrue(self.prescription_order.invoice_status == 'no', 'Prescription: RX status after invoicing should be "nothing to invoice"')
        self.assertTrue(len(self.prescription_order.invoice_ids) == 1, 'Prescription: invoice is missing')
        self.prescription_order.order_line._compute_product_updatable()
        self.assertFalse(self.prescription_order.order_line[0].product_updatable)

        # deliver lines except 'time and material' then invoice again
        for line in self.prescription_order.order_line:
            line.qty_delivered = 2 if line.product_id.expense_policy == 'no' else 0
        self.assertTrue(self.prescription_order.invoice_status == 'to invoice', 'Prescription: RX status after delivery should be "to invoice"')
        invoice2 = self.prescription_order._create_invoices()
        self.assertEqual(len(invoice2.invoice_line_ids), 2, 'Prescription: second invoice is missing lines')
        self.assertEqual(invoice2.amount_total, 500.0, 'Prescription: second invoice total amount is wrong')
        self.assertTrue(self.prescription_order.invoice_status == 'invoiced', 'Prescription: RX status after invoicing everything should be "invoiced"')
        self.assertTrue(len(self.prescription_order.invoice_ids) == 2, 'Prescription: invoice is missing')

        # go over the sold quantity
        self.rxl_serv_order.write({'qty_delivered': 10})
        self.assertTrue(self.prescription_order.invoice_status == 'upselling', 'Prescription: RX status after increasing delivered qty higher than ordered qty should be "upselling"')

        # upsell and invoice
        self.rxl_serv_order.write({'product_uom_qty': 10})

        # There is a bug with `new` and `_origin`
        # If you create a first new from a record, then change a value on the origin record, than create another new,
        # this other new wont have the updated value of the origin record, but the one from the previous new
        # Here the problem lies in the use of `new` in `move = self_ctx.new(new_vals)`,
        # and the fact this method is called multiple times in the same transaction test case.
        # Here, we update `qty_delivered` on the origin record, but the `new` records which are in cache with this order line
        # as origin are not updated, nor the fields that depends on it.
        self.env.flush_all()
        self.env.invalidate_all()

        invoice3 = self.prescription_order._create_invoices()
        self.assertEqual(len(invoice3.invoice_line_ids), 1, 'Prescription: third invoice is missing lines')
        self.assertEqual(invoice3.amount_total, 720.0, 'Prescription: second invoice total amount is wrong')
        self.assertTrue(self.prescription_order.invoice_status == 'invoiced', 'Prescription: RX status after invoicing everything (including the upsel) should be "invoiced"')

    def test_rx_create_multicompany(self):
        """Check that only taxes of the right company are applied on the lines."""
        # Preparing test Data
        product_shared = self.env['product.template'].create({
            'name': 'shared product',
            'invoice_policy': 'order',
            'taxes_id': [(6, False, (self.company_data['default_tax_prescription'] + self.company_data_2['default_tax_prescription']).ids)],
            'property_account_income_id': self.company_data['default_account_revenue'].id,
        })

        rx_1 = self.env['prescription.order'].with_user(self.company_data['default_user_personnel']).create({
            'partner_id': self.env['res.partner'].create({'name': 'A partner'}).id,
            'company_id': self.company_data['company'].id,
        })
        rx_1.write({
            'order_line': [Command.create({'product_id': product_shared.product_variant_id.id})],
        })
        self.assertEqual(rx_1.order_line.product_uom_qty, 1)

        self.assertEqual(rx_1.order_line.tax_id, self.company_data['default_tax_prescription'],
            'Only taxes from the right company are put by default')
        rx_1.action_confirm()
        # i'm not interested in groups/acls, but in the multi-company flow only
        # the sudo is there for that and does not impact the invoice that gets created
        # the goal here is to invoice in company 1 (because the order is in company 1) while being
        # 'mainly' in company 2 (through the context), the invoice should be in company 1
        inv = rx_1.sudo().with_context(
            allowed_company_ids=(self.company_data['company'] + self.company_data_2['company']).ids
        )._create_invoices()
        self.assertEqual(
            inv.company_id,
            self.company_data['company'],
            'invoices should be created in the company of the RX, not the main company of the context')

    def test_partial_invoicing_interaction_with_invoicing_switch_threshold(self):
        """ Let's say you partially invoice a RX, let's call the resuling invoice 'A'. Now if you change the
            'Invoicing Switch Threshold' such that the invoice date of 'A' is before the new threshold,
            the RX should still take invoice 'A' into account.
        """
        if not self.env['ir.module.module'].search([('name', '=', 'account_accountant'), ('state', '=', 'installed')]):
            self.skipTest("This test requires the installation of the account_account module")

        prescription_order = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.company_data['product_delivery_no'].id,
                    'product_uom_qty': 20,
                }),
            ],
        })
        line = prescription_order.order_line[0]

        prescription_order.action_confirm()

        line.qty_delivered = 10

        invoice = prescription_order._create_invoices()
        invoice.action_post()

        self.assertEqual(line.qty_invoiced, 10)

        self.env['res.config.settings'].create({
            'invoicing_switch_threshold': fields.Date.add(invoice.invoice_date, days=30),
        }).execute()

        invoice.invalidate_model(fnames=['payment_state'])

        self.assertEqual(line.qty_invoiced, 10)
        line.qty_delivered = 15
        self.assertEqual(line.qty_invoiced, 10)

    def test_prescriptionperson_in_invoice_followers(self):
        """
        Test if the prescriptionperson is in the followers list of invoice created from RX
        """
        # create a prescriptionperson
        prescriptionperson = self.env['res.users'].create({
            'name': 'Prescription Person',
            'login': 'prescriptionperson',
            'email': 'test@test.com',
            'groups_id': [(6, 0, [self.env.ref('pod_prescription_team.group_prescription_personnel').id])]
        })

        # create a RX and generate invoice from it
        prescription_order = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'user_id': prescriptionperson.id,
            'order_line': [(0, 0, {
                'product_id': self.company_data['product_order_no'].id,
                'product_uom_qty': 1,
            })]
        })
        prescription_order.action_confirm()
        invoice = prescription_order._create_invoices(final=True)

        # check if the prescriptionperson is in the followers list of invoice created from RX
        self.assertIn(prescriptionperson.partner_id, invoice.message_partner_ids, 'Prescription Person not in the followers list of '
                                                                           'invoice created from RX')
    def test_amount_to_invoice_multiple_rx(self):
        """ Testing creating two RXs with the same customer and invoicing them together. We have to ensure
            that the amount to invoice is correct for each RX.
        """
        prescription_order_1 = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.company_data['product_delivery_no'].id,
                    'product_uom_qty': 10,
                }),
            ],
        })
        prescription_order_2 = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.company_data['product_delivery_no'].id,
                    'product_uom_qty': 20,
                }),
            ],
        })

        prescription_order_1.action_confirm()
        prescription_order_2.action_confirm()
        prescription_order_1.order_line.qty_delivered = 10
        prescription_order_2.order_line.qty_delivered = 20

        self.env['prescription.advance.payment.inv'].create({
            'advance_payment_method': 'delivered',
            'prescription_order_ids': [Command.set((prescription_order_1 + prescription_order_2).ids)],
        }).create_invoices()

        prescription_order_1.invoice_ids.action_post()

        self.assertEqual(prescription_order_1.amount_to_invoice, 0.0)
        self.assertEqual(prescription_order_2.amount_to_invoice, 0.0)

    def test_amount_to_invoice_one_line_multiple_rx(self):
        """ Testing creating two RXs linked to the same invoice line. Drawback: the substracted
            amount to the amount_total will take both prescription order into account.
        """
        prescription_order_1 = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.company_data['product_delivery_no'].id,
                    'product_uom_qty': 10,
                }),
            ],
        })
        prescription_order_2 = self.env['prescription.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.company_data['product_delivery_no'].id,
                    'product_uom_qty': 20,
                }),
            ],
        })

        prescription_order_1.action_confirm()
        prescription_order_2.action_confirm()
        prescription_order_1.order_line.qty_delivered = 10
        prescription_order_2.order_line.qty_delivered = 20

        self.env['prescription.advance.payment.inv'].create({
            'advance_payment_method': 'delivered',
            'prescription_order_ids': [Command.set((prescription_order_2).ids)],
        }).create_invoices()

        prescription_order_1.invoice_ids = prescription_order_2.invoice_ids
        prescription_order_1.invoice_ids.line_ids.prescription_line_ids += prescription_order_1.order_line

        prescription_order_1.invoice_ids.action_post()

        self.assertEqual(prescription_order_1.amount_to_invoice, -700.0)
        self.assertEqual(prescription_order_2.amount_to_invoice, 0.0)
