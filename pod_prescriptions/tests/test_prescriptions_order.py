# -*- coding: utf-8 -*-

from datetime import timedelta
from freezegun import freeze_time

from odoo import fields
from odoo.fields import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged, Form
from odoo.tools import float_compare

from odoo.addons.pod_prescriptions.tests.common import PrescriptionCommon


@tagged('post_install', '-at_install')
class TestPrescriptionOrder(PrescriptionCommon):

    # Those tests do not rely on accounting common on purpose
    #   If you need the accounting setup, use other classes (TestPrescriptionToInvoice probably)

    def test_computes_auto_fill(self):
        free_product, dummy_product = self.env['product.product'].create([{
            'name': 'Free product',
            'list_price': 0.0,
        }, {
            'name': 'Dummy product',
            'list_price': 0.0,
        }])
        # Test pre-computes of lines with order
        order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'display_type': 'line_section',
                    'name': 'Dummy section',
                }),
                Command.create({
                    'display_type': 'line_section',
                    'name': 'Dummy section',
                }),
                Command.create({
                    'product_id': free_product.id,
                }),
                Command.create({
                    'product_id': dummy_product.id,
                })
            ]
        })

        # Test pre-computes of lines creation alone
        # Ensures the creation works fine even if the computes
        # are triggered after the defaults
        order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
        })
        self.env['prescriptions.order.line'].create([
            {
                'display_type': 'line_section',
                'name': 'Dummy section',
                'order_id': order.id,
            }, {
                'display_type': 'line_section',
                'name': 'Dummy section',
                'order_id': order.id,
            }, {
                'product_id': free_product.id,
                'order_id': order.id,
            }, {
                'product_id': dummy_product.id,
                'order_id': order.id,
            }
        ])

    def test_prescriptions_order_standard_flow(self):
        self.assertEqual(self.prescriptions_order.amount_total, 725.0, 'Prescription: total amount is wrong')
        self.prescriptions_order.order_line._compute_product_updatable()
        self.assertTrue(self.prescriptions_order.order_line[0].product_updatable)

        # send quotation
        email_act = self.prescriptions_order.action_quotation_send()
        email_ctx = email_act.get('context', {})
        self.prescriptions_order.with_context(**email_ctx).message_post_with_source(
            self.env['mail.template'].browse(email_ctx.get('default_template_id')),
            subtype_xmlid='mail.mt_comment',
        )
        self.assertTrue(self.prescriptions_order.state == 'sent', 'Prescription: state after sending is wrong')
        self.prescriptions_order.order_line._compute_product_updatable()
        self.assertTrue(self.prescriptions_order.order_line[0].product_updatable)

        # confirm quotation
        self.prescriptions_order.action_confirm()
        self.assertTrue(self.prescriptions_order.state == 'sales')
        self.assertTrue(self.prescriptions_order.invoice_status == 'to invoice')

    def test_prescriptions_order_send_to_self(self):
        # when sender(logged in user) is also present in recipients of the mail composer,
        # user should receive mail.
        prescriptions_order = self.env['prescriptions.order'].with_user(self.prescriptions_user).create({
            'partner_id': self.prescriptions_user.partner_id.id,
        })
        email_ctx = prescriptions_order.action_quotation_send().get('context', {})
        # We need to prevent auto mail deletion, and so we copy the template and send the mail with
        # added configuration in copied template. It will allow us to check whether mail is being
        # sent to to author or not (in case author is present in 'Recipients' of composer).
        mail_template = self.env['mail.template'].browse(email_ctx.get('default_template_id')).copy({'auto_delete': False})
        # send the mail with same user as customer
        prescriptions_order.with_context(**email_ctx).with_user(self.prescriptions_user).message_post_with_source(
            mail_template,
            subtype_xmlid='mail.mt_comment',
        )
        self.assertTrue(prescriptions_order.state == 'sent', 'Prescription : state should be changed to sent')
        mail_message = prescriptions_order.message_ids[0]
        self.assertEqual(mail_message.author_id, prescriptions_order.partner_id, 'Prescription: author should be same as customer')
        self.assertEqual(mail_message.author_id, mail_message.partner_ids, 'Prescription: author should be in composer recipients thanks to "partner_to" field set on template')
        self.assertEqual(mail_message.partner_ids, mail_message.sudo().mail_ids.recipient_ids, 'Prescription: author should receive mail due to presence in composer recipients')

    def test_invoice_state_when_ordered_quantity_is_negative(self):
        """When you invoice a RX line with a product that is invoiced on ordered quantities and has negative ordered quantity,
        this test ensures that the  invoicing status of the RX line is 'invoiced' (and not 'upselling')."""
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': -1,
            })]
        })
        prescriptions_order.action_confirm()
        prescriptions_order._create_invoices(final=True)
        self.assertTrue(prescriptions_order.invoice_status == 'invoiced', 'Prescription: The invoicing status of the RX should be "invoiced"')

    def test_prescriptions_sequence(self):
        self.env['ir.sequence'].search([
            ('code', '=', 'prescriptions.order'),
        ]).write({
            'use_date_range': True, 'prefix': 'RX/%(range_year)s/',
        })
        prescriptions_order = self.prescriptions_order.copy({'date_order': '2019-01-01'})
        self.assertTrue(prescriptions_order.name.startswith('RX/2019/'))
        prescriptions_order = self.prescriptions_order.copy({'date_order': '2020-01-01'})
        self.assertTrue(prescriptions_order.name.startswith('RX/2020/'))
        # In EU/BXL tz, this is actually already 01/01/2020
        prescriptions_order = self.prescriptions_order.with_context(tz='Europe/Brussels').copy({'date_order': '2019-12-31 23:30:00'})
        self.assertTrue(prescriptions_order.name.startswith('RX/2020/'))

    def test_unlink_cancel(self):
        """ Test deleting and cancelling prescriptions orders depending on their state and on the user's rights """
        # RX in state 'draft' can be deleted
        rx_copy = self.prescriptions_order.copy()
        with self.assertRaises(AccessError):
            rx_copy.with_user(self.prescriptions_user).unlink()
        self.assertTrue(rx_copy.unlink(), 'Prescription: deleting a quotation should be possible')

        # RX in state 'cancel' can be deleted
        rx_copy = self.prescriptions_order.copy()
        rx_copy.action_confirm()
        self.assertTrue(rx_copy.state == 'sales', 'Prescription: RX should be in state "prescriptions"')
        rx_copy._action_cancel()
        self.assertTrue(rx_copy.state == 'cancel', 'Prescription: RX should be in state "cancel"')
        with self.assertRaises(AccessError):
            rx_copy.with_user(self.prescriptions_user).unlink()
        self.assertTrue(rx_copy.unlink(), 'Prescription: deleting a cancelled RX should be possible')

        # RX in state 'sales' cannot be deleted
        self.prescriptions_order.action_confirm()
        self.assertTrue(self.prescriptions_order.state == 'sales', 'Prescription: RX should be in state "prescriptions"')
        with self.assertRaises(UserError):
            self.prescriptions_order.unlink()

        self.prescriptions_order.action_lock()
        self.assertTrue(self.prescriptions_order.state == 'sales')
        self.assertTrue(self.prescriptions_order.locked)
        with self.assertRaises(UserError):
            self.prescriptions_order.unlink()

    def test_compute_packaging_00(self):
        """Create a RX and use packaging. Check we suggested suitable packaging
        according to the product_qty. Also check product_qty or product_packaging
        are correctly calculated when one of them changed.
        """
        # Required for `product_packaging_qty` to be visible in the view
        self.env.user.groups_id += self.env.ref('product.group_stock_packaging')
        packaging_single, packaging_dozen = self.env['product.packaging'].create([{
            'name': "I'm a packaging",
            'product_id': self.product.id,
            'qty': 1.0,
        }, {
            'name': "I'm also a packaging",
            'product_id': self.product.id,
            'qty': 12.0,
        }])

        rx = self.empty_order
        rx_form = Form(rx)
        with rx_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1.0
        rx_form.save()
        self.assertEqual(rx.order_line.product_packaging_id, packaging_single)
        self.assertEqual(rx.order_line.product_packaging_qty, 1.0)
        with rx_form.order_line.edit(0) as line:
            line.product_packaging_qty = 2.0
        rx_form.save()
        self.assertEqual(rx.order_line.product_uom_qty, 2.0)

        with rx_form.order_line.edit(0) as line:
            line.product_uom_qty = 24.0
        rx_form.save()
        self.assertEqual(rx.order_line.product_packaging_id, packaging_dozen)
        self.assertEqual(rx.order_line.product_packaging_qty, 2.0)
        with rx_form.order_line.edit(0) as line:
            line.product_packaging_qty = 1.0
        rx_form.save()
        self.assertEqual(rx.order_line.product_uom_qty, 12)

        packaging_pack_of_10 = self.env['product.packaging'].create({
            'name': "PackOf10",
            'product_id': self.product.id,
            'qty': 10.0,
        })
        packaging_pack_of_20 = self.env['product.packaging'].create({
            'name': "PackOf20",
            'product_id': self.product.id,
            'qty': 20.0,
        })

        rx2 = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
        })
        rx2_form = Form(rx2)
        with rx2_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 10
        rx2_form.save()
        self.assertEqual(rx2.order_line.product_packaging_id.id, packaging_pack_of_10.id)
        self.assertEqual(rx2.order_line.product_packaging_qty, 1.0)

        with rx2_form.order_line.edit(0) as line:
            line.product_packaging_qty = 2
        rx2_form.save()
        self.assertEqual(rx2.order_line.product_uom_qty, 20)
        # we should have 2 pack of 10, as we've set the package_qty manually,
        # we shouldn't recompute the packaging_id, since the package_qty is protected,
        # therefor cannot be recomputed during the same transaction, which could lead
        # to an incorrect line like (qty=20,pack_qty=2,pack_id=PackOf20)
        self.assertEqual(rx2.order_line.product_packaging_qty, 2)
        self.assertEqual(rx2.order_line.product_packaging_id.id, packaging_pack_of_10.id)

        with rx2_form.order_line.edit(0) as line:
            line.product_packaging_id = packaging_pack_of_20
        rx2_form.save()
        self.assertEqual(rx2.order_line.product_uom_qty, 20)
        # we should have 1 pack of 20, as we've set the package type manually
        self.assertEqual(rx2.order_line.product_packaging_qty, 1)
        self.assertEqual(rx2.order_line.product_packaging_id.id, packaging_pack_of_20.id)

    def test_compute_packaging_01(self):
        """Create a RX and use packaging in a multicompany environment.
        Ensure any suggested packaging matches the RX's.
        """
        company2 = self.env['res.company'].create([{'name': 'Company 2'}])
        generic_single_pack = self.env['product.packaging'].create({
            'name': "single pack",
            'product_id': self.product.id,
            'qty': 1.0,
            'company_id': False,
        })
        company2_pack_of_10 = self.env['product.packaging'].create({
            'name': "pack of 10 by Company 2",
            'product_id': self.product.id,
            'qty': 10.0,
            'company_id': company2.id,
        })

        rx1 = self.empty_order
        rx1_form = Form(rx1)
        with rx1_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 10.0
        rx1_form.save()
        self.assertEqual(rx1.order_line.product_packaging_id, generic_single_pack)
        self.assertEqual(rx1.order_line.product_packaging_qty, 10.0)

        rx2 = self.env['prescriptions.order'].with_company(company2).create({
            'partner_id': self.partner.id,
        })
        rx2_form = Form(rx2)
        with rx2_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 10.0
        rx2_form.save()
        self.assertEqual(rx2.order_line.product_packaging_id, company2_pack_of_10)
        self.assertEqual(rx2.order_line.product_packaging_qty, 1.0)

    def _create_prescriptions_order(self):
        """Create dummy prescriptions order (without lines)"""
        return self.env['prescriptions.order'].with_context(
            default_prescriptions_order_template_id=False
            # Do not modify test behavior even if pod_prescriptions_management is installed
        ).create({
            'partner_id': self.partner.id,
        })

    def test_invoicing_terms(self):
        # Enable invoicing terms
        self.env['ir.config_parameter'].sudo().set_param('account.use_invoice_terms', True)

        # Plain invoice terms
        self.env.company.terms_type = 'plain'
        self.env.company.invoice_terms = "Coin coin"
        prescriptions_order = self._create_prescriptions_order()
        self.assertEqual(prescriptions_order.note, "<p>Coin coin</p>")

        # Html invoice terms (/terms page)
        self.env.company.terms_type = 'html'
        prescriptions_order = self._create_prescriptions_order()
        self.assertTrue(prescriptions_order.note.startswith("<p>Terms &amp; Conditions: "))

    def test_validity_days(self):
        self.env.company.quotation_validity_days = 5
        with freeze_time("2020-05-02"):
            prescriptions_order = self._create_prescriptions_order()

            self.assertEqual(prescriptions_order.validity_date, fields.Date.today() + timedelta(days=5))
        self.env.company.quotation_validity_days = 0
        prescriptions_order = self._create_prescriptions_order()
        self.assertFalse(
            prescriptions_order.validity_date,
            "No validity date must be specified if the company validity duration is 0")

    def test_rx_names(self):
        """Test custom context key for display_name & name_search.

        Note: this key is used in prescriptions_expense & prescriptions_timesheet modules.
        """
        PrescriptionOrder = self.env['prescriptions.order'].with_context(prescriptions_show_partner_name=True)

        res = PrescriptionOrder.name_search(name=self.prescriptions_order.partner_id.name)
        self.assertEqual(res[0][0], self.prescriptions_order.id)

        self.assertNotIn(self.prescriptions_order.partner_id.name, self.prescriptions_order.display_name)
        self.assertIn(
            self.prescriptions_order.partner_id.name,
            self.prescriptions_order.with_context(prescriptions_show_partner_name=True).display_name)

    def test_state_changes(self):
        """Test some untested state changes methods & logic."""
        self.prescriptions_order.action_quotation_sent()

        self.assertEqual(self.prescriptions_order.state, 'sent')
        self.assertIn(self.prescriptions_order.partner_id, self.prescriptions_order.message_follower_ids.partner_id)

        self.env.user.groups_id += self.env.ref('pod_prescriptions.group_auto_done_setting')
        self.prescriptions_order.action_confirm()
        self.assertEqual(self.prescriptions_order.state, 'sales')
        self.assertTrue(self.prescriptions_order.locked)
        with self.assertRaises(UserError):
            self.prescriptions_order.action_confirm()

        self.prescriptions_order.action_unlock()
        self.assertEqual(self.prescriptions_order.state, 'sales')

    def test_rxl_name_search(self):
        # Shouldn't raise
        self.env['prescriptions.order']._search([('order_line', 'ilike', 'product')])

        name_search_data = self.env['prescriptions.order.line'].name_search(name=self.prescriptions_order.name)
        rxl_ids_found = dict(name_search_data).keys()
        self.assertEqual(list(rxl_ids_found), self.prescriptions_order.order_line.ids)

    def test_zero_quantity(self):
        """
            If the quantity set is 0 it should remain to 0
            Test that changing the uom do not change the quantity
        """
        order_line = self.prescriptions_order.order_line[0]
        order_line.product_uom_qty = 0.0
        order_line.product_uom = self.uom_dozen
        self.assertEqual(order_line.product_uom_qty, 0.0)

    def test_discount_rounding(self):
        """
            Check the discount is properly rounded and the price subtotal
            computed with this rounded discount
        """
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 192,
                'discount': 74.246,
            })]
        })
        self.assertEqual(prescriptions_order.order_line.price_subtotal, 49.44, "Subtotal should be equal to 192 * (1 - 0.7425)")
        self.assertEqual(prescriptions_order.order_line.discount, 74.25)

    def test_tax_amount_rounding(self):
        """ Check order amounts are rounded according to settings """

        tax_a = self.env['account.tax'].create({
            'name': 'Test tax',
            'type_tax_use': 'sales',
            'price_include': False,
            'amount_type': 'percent',
            'amount': 15.0,
        })

        # Test Round per Line (default)
        self.env.company.tax_calculation_rounding_method = 'round_per_line'
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
            ],
        })
        self.assertEqual(prescriptions_order.amount_total, 15.42, "")

        # Test Round Globally
        self.env.company.tax_calculation_rounding_method = 'round_globally'
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
            ],
        })
        self.assertEqual(prescriptions_order.amount_total, 15.41, "")


@tagged('post_install', '-at_install')
class TestPrescriptionsTeam(PrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # set up users
        cls.prescriptions_team_2 = cls.env['crm.team'].create({
            'name': 'Test Prescriptions Team (2)',
        })
        cls.user_in_team = cls.env['res.users'].create({
            'email': 'team0user@example.com',
            'login': 'team0user',
            'name': 'User in Team 0',
        })
        cls.prescriptions_team.write({'member_ids': [4, cls.user_in_team.id]})
        cls.user_not_in_team = cls.env['res.users'].create({
            'email': 'noteamuser@example.com',
            'login': 'noteamuser',
            'name': 'User Not In Team',
        })

    def test_assign_prescriptions_team_from_partner_user(self):
        """Use the team from the customer's prescriptions person, if it is set"""
        partner = self.env['res.partner'].create({
            'name': 'Customer of User In Team',
            'user_id': self.user_in_team.id,
            'team_id': self.prescriptions_team_2.id,
        })
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': partner.id,
        })
        self.assertEqual(prescriptions_order.team_id.id, self.prescriptions_team.id, 'Should assign to team of prescriptions person')

    def test_assign_prescriptions_team_from_partner_team(self):
        """If no team set on the customer's prescriptions person, fall back to the customer's team"""
        partner = self.env['res.partner'].create({
            'name': 'Customer of User Not In Team',
            'user_id': self.user_not_in_team.id,
            'team_id': self.prescriptions_team_2.id,
        })
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': partner.id,
        })
        self.assertEqual(prescriptions_order.team_id.id, self.prescriptions_team_2.id, 'Should assign to team of partner')

    def test_assign_prescriptions_team_when_changing_user(self):
        """When we assign a prescriptions person, change the team on the prescriptions order to their team"""
        prescriptions_order = self.env['prescriptions.order'].create({
            'user_id': self.user_not_in_team.id,
            'partner_id': self.partner.id,
            'team_id': self.prescriptions_team_2.id
        })
        prescriptions_order.user_id = self.user_in_team
        self.assertEqual(prescriptions_order.team_id.id, self.prescriptions_team.id, 'Should assign to team of prescriptions person')

    def test_keep_prescriptions_team_when_changing_user_with_no_team(self):
        """When we assign a prescriptions person that has no team, do not reset the team to default"""
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'team_id': self.prescriptions_team_2.id
        })
        prescriptions_order.user_id = self.user_not_in_team
        self.assertEqual(prescriptions_order.team_id.id, self.prescriptions_team_2.id, 'Should not reset the team to default')

    def test_prescriptions_order_analytic_distribution_change(self):
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')

        analytic_plan = self.env['account.analytic.plan'].create({'name': 'Plan Test'})
        analytic_account_super = self.env['account.analytic.account'].create({'name': 'Super Account', 'plan_id': analytic_plan.id})
        analytic_account_great = self.env['account.analytic.account'].create({'name': 'Great Account', 'plan_id': analytic_plan.id})
        super_product = self.env['product.product'].create({'name': 'Super Product'})
        great_product = self.env['product.product'].create({'name': 'Great Product'})
        product_no_account = self.env['product.product'].create({'name': 'Product No Account'})
        self.env['account.analytic.distribution.model'].create([
            {
                'analytic_distribution': {analytic_account_super.id: 100},
                'product_id': super_product.id,
            },
            {
                'analytic_distribution': {analytic_account_great.id: 100},
                'product_id': great_product.id,
            },
        ])
        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        rxl = self.env['prescriptions.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': prescriptions_order.id,
        })

        self.assertEqual(rxl.analytic_distribution, {str(analytic_account_super.id): 100}, "The analytic distribution should be set to Super Account")
        rxl.write({'product_id': great_product.id})
        self.assertEqual(rxl.analytic_distribution, {str(analytic_account_great.id): 100}, "The analytic distribution should be set to Great Account")

        rx_no_analytic_account = self.env['prescriptions.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        rxl_no_analytic_account = self.env['prescriptions.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': rx_no_analytic_account.id,
            'analytic_distribution': False,
        })
        rx_no_analytic_account.action_confirm()
        self.assertFalse(rxl_no_analytic_account.analytic_distribution, "The compute should not overwrite what the user has set.")

        prescriptions_order.action_confirm()
        rxl_on_confirmed_order = self.env['prescriptions.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': prescriptions_order.id,
        })

        self.assertEqual(
            rxl_on_confirmed_order.analytic_distribution,
            {str(analytic_account_super.id): 100},
            "The analytic distribution should be set to Super Account, even for confirmed orders"
        )


    def test_cannot_assign_tax_of_mismatch_company(self):
        """ Test that rxl cannot have assigned tax belonging to a different company from that of the prescriptions order. """
        company_a = self.env['res.company'].create({'name': 'A'})
        company_b = self.env['res.company'].create({'name': 'B'})
        tax_group_a = self.env['account.tax.group'].create({'name': 'A', 'company_id': company_a.id})
        tax_group_b = self.env['account.tax.group'].create({'name': 'B', 'company_id': company_b.id})
        country = self.env['res.country'].search([])[0]

        tax_a = self.env['account.tax'].create({
            'name': 'A',
            'amount': 10,
            'company_id': company_a.id,
            'tax_group_id': tax_group_a.id,
            'country_id': country.id,
        })
        tax_b = self.env['account.tax'].create({
            'name': 'B',
            'amount': 10,
            'company_id': company_b.id,
            'tax_group_id': tax_group_b.id,
            'country_id': country.id,
        })

        prescriptions_order = self.env['prescriptions.order'].create({
            'partner_id': self.partner.id,
            'company_id': company_a.id
        })
        product = self.env['product.product'].create({'name': 'Product'})

        # In sudo to simulate an user that have access to both companies.
        rxl = self.env['prescriptions.order.line'].sudo().create({
            'name': product.name,
            'product_id': product.id,
            'order_id': prescriptions_order.id,
            'tax_id': tax_a,
        })

        with self.assertRaises(UserError):
            rxl.tax_id = tax_b

    def test_downpayment_amount_constraints(self):
        """Down payment amounts should be in the interval ]0, 1]."""

        self.prescriptions_order.require_payment = True
        with self.assertRaises(ValidationError):
            self.prescriptions_order.prepayment_percent = -1
        with self.assertRaises(ValidationError):
            self.prescriptions_order.prepayment_percent = 1.01
