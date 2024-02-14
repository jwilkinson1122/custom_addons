# -*- coding: utf-8 -*-


from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestPrescriptionOnchanges(TransactionCase):

    def test_prescription_warnings(self):
        """Test warnings & SO/SOL updates when partner/products with prescription warnings are used."""
        partner_with_warning = self.env['res.partner'].create({
            'name': 'Test', 'prescription_warn': 'warning', 'prescription_warn_msg': 'Highly infectious disease'})
        partner_with_block_warning = self.env['res.partner'].create({
            'name': 'Test2', 'prescription_warn': 'block', 'prescription_warn_msg': 'Cannot afford our services'})

        prescription_order = self.env['prescription.order'].create({'partner_id': partner_with_warning.id})
        warning = prescription_order._onchange_partner_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test",
                'message': partner_with_warning.prescription_warn_msg,
            },
        })

        prescription_order.partner_id = partner_with_block_warning
        warning = prescription_order._onchange_partner_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test2",
                'message': partner_with_block_warning.prescription_warn_msg,
            },
        })

        # Verify partner-related fields have been correctly reset
        self.assertFalse(prescription_order.partner_id.id)
        self.assertFalse(prescription_order.partner_invoice_id.id)
        self.assertFalse(prescription_order.partner_shipping_id.id)
        self.assertFalse(prescription_order.pricelist_id.id)

        # Reuse non blocking partner for product warning tests
        prescription_order.partner_id = partner_with_warning
        product_with_warning = self.env['product.product'].create({
            'name': 'Test Product', 'prescription_line_warn': 'warning', 'prescription_line_warn_msg': 'Highly corrosive'})
        product_with_block_warning = self.env['product.product'].create({
            'name': 'Test Product (2)', 'prescription_line_warn': 'block', 'prescription_line_warn_msg': 'Not produced anymore'})

        prescription_order_line = self.env['prescription.order.line'].create({
            'order_id': prescription_order.id,
            'product_id': product_with_warning.id,
        })
        warning = prescription_order_line._onchange_product_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test Product",
                'message': product_with_warning.prescription_line_warn_msg,
            },
        })

        prescription_order_line.product_id = product_with_block_warning
        warning = prescription_order_line._onchange_product_id_warning()

        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test Product (2)",
                'message': product_with_block_warning.prescription_line_warn_msg,
            },
        })

        self.assertFalse(prescription_order_line.product_id.id)
