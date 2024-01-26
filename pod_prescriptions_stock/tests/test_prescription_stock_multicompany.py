# -*- coding: utf-8 -*-

from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import ValuationReconciliationTestCommon
from odoo.addons.pod_prescriptions.tests.common import TestPrescriptionCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestPrescriptionStockMultiCompany(TestPrescriptionCommon, ValuationReconciliationTestCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.warehouse_A = cls.company_data['default_warehouse']
        cls.warehouse_A2 = cls.env['stock.warehouse'].create({
            'name': 'WH B',
            'code': 'WHB',
            'company_id': cls.env.company.id,
            'partner_id': cls.env.company.partner_id.id,
        })
        cls.warehouse_B = cls.company_data_2['default_warehouse']

        cls.env.user.groups_id |= cls.env.ref('stock.group_stock_user')
        cls.env.user.groups_id |= cls.env.ref('stock.group_stock_multi_locations')
        cls.env.user.groups_id |= cls.env.ref('pod_prescriptions_team.group_prescriptions_prescriptionsman')

        cls.env.user.with_company(cls.company_data['company']).property_pod_warehouse_id = cls.warehouse_A.id
        cls.env.user.with_company(cls.company_data_2['company']).property_pod_warehouse_id = cls.warehouse_B.id

    def test_warehouse_definition_on_rx(self):

        partner = self.partner_a
        product = self.test_product_order

        prescriptions_order_vals = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'user_id': False,
            'company_id': self.env.company.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 10,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price})],
            'pricelist_id': self.company_data['default_pricelist'].id,
        }
        prescriptions_order = self.env['prescriptions.order']

        rx_no_user = prescriptions_order.create(prescriptions_order_vals)
        self.assertFalse(rx_no_user.user_id.property_pod_warehouse_id)
        self.assertEqual(rx_no_user.pod_warehouse_id.id, self.warehouse_A.id)

        prescriptions_order_vals2 = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'company_id': self.env.company.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 10,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price})],
            'pricelist_id': self.company_data['default_pricelist'].id,
        }
        rx_company_A = prescriptions_order.with_company(self.env.company).create(prescriptions_order_vals2)
        self.assertEqual(rx_company_A.pod_warehouse_id.id, self.warehouse_A.id)

        prescriptions_order_vals3 = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'company_id': self.company_data_2['company'].id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 10,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price})],
            'pricelist_id': self.company_data['default_pricelist'].id,
        }
        rx_company_B = prescriptions_order.with_company(self.company_data_2['company']).create(prescriptions_order_vals3)
        self.assertEqual(rx_company_B.pod_warehouse_id.id, self.warehouse_B.id)
