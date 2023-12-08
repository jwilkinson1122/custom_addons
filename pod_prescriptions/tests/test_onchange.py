# -*- coding: utf-8 -*-


from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestPrescriptionOnchanges(TransactionCase):

    def test_prescriptions_warnings(self):
        """Test warnings & RX/RXL updates when partner/products with prescriptions warnings are used."""
        partner_with_warning = self.env['res.partner'].create({
            'name': 'Test', 'prescriptions_warn': 'warning', 'prescriptions_warn_msg': 'Highly infectious disease'})
        partner_with_block_warning = self.env['res.partner'].create({
            'name': 'Test2', 'prescriptions_warn': 'block', 'prescriptions_warn_msg': 'Cannot afford our services'})

        prescriptions_order = self.env['prescriptions.order'].create({'partner_id': partner_with_warning.id})
        warning = prescriptions_order._onchange_partner_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test",
                'message': partner_with_warning.prescriptions_warn_msg,
            },
        })

        prescriptions_order.partner_id = partner_with_block_warning
        warning = prescriptions_order._onchange_partner_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test2",
                'message': partner_with_block_warning.prescriptions_warn_msg,
            },
        })

        # Verify partner-related fields have been correctly reset
        self.assertFalse(prescriptions_order.partner_id.id)
        self.assertFalse(prescriptions_order.partner_invoice_id.id)
        self.assertFalse(prescriptions_order.partner_shipping_id.id)
        self.assertFalse(prescriptions_order.pricelist_id.id)

        # Reuse non blocking partner for product warning tests
        prescriptions_order.partner_id = partner_with_warning
        product_with_warning = self.env['product.product'].create({
            'name': 'Test Product', 'prescriptions_line_warn': 'warning', 'prescriptions_line_warn_msg': 'Highly corrosive'})
        product_with_block_warning = self.env['product.product'].create({
            'name': 'Test Product (2)', 'prescriptions_line_warn': 'block', 'prescriptions_line_warn_msg': 'Not produced anymore'})

        prescriptions_order_line = self.env['prescriptions.order.line'].create({
            'order_id': prescriptions_order.id,
            'product_id': product_with_warning.id,
        })
        warning = prescriptions_order_line._onchange_product_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test Product",
                'message': product_with_warning.prescriptions_line_warn_msg,
            },
        })

        prescriptions_order_line.product_id = product_with_block_warning
        warning = prescriptions_order_line._onchange_product_id_warning()

        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test Product (2)",
                'message': product_with_block_warning.prescriptions_line_warn_msg,
            },
        })

        self.assertFalse(prescriptions_order_line.product_id.id)
