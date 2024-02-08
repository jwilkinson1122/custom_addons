

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.pod_prescriptions.tests.common import PrescriptionCommon


@tagged('post_install', '-at_install')
class TestPrescriptionOrderDiscount(PrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.env['prescriptions.order.discount'].create({
            'prescriptions_order_id': cls.prescriptions_order.id,
            'discount_type': 'amount',
        })

    def test_amount(self):
        self.wizard.write({
            'discount_amount': 55,
            'discount_type': 'amount',
        })
        self.wizard.action_apply_discount()

        discount_line = self.prescriptions_order.order_line[-1]
        self.assertEqual(discount_line.price_unit, -55)
        self.assertEqual(discount_line.product_uom_qty, 1.0)
        self.assertFalse(discount_line.tax_id)

    def test_so_discount(self):
        solines = self.prescriptions_order.order_line
        amount_before_discount = self.prescriptions_order.amount_total
        self.assertEqual(len(solines), 2)

        # No taxes
        solines.tax_id = [Command.clear()]
        self.wizard.write({
            'discount_percentage': 0.5,  # 50%
            'discount_type': 'so_discount',
        })
        self.wizard.action_apply_discount()

        discount_line = self.prescriptions_order.order_line[-1]
        self.assertAlmostEqual(discount_line.price_unit, -amount_before_discount*0.5)
        self.assertFalse(discount_line.tax_id)
        self.assertEqual(discount_line.product_uom_qty, 1.0)

        # One tax group
        discount_line.unlink()
        dumb_tax = self.env['account.tax'].create({'name': 'test'})
        solines.tax_id = dumb_tax
        self.wizard.action_apply_discount()

        discount_line = self.prescriptions_order.order_line - solines
        discount_line.ensure_one()
        self.assertAlmostEqual(discount_line.price_unit, -amount_before_discount*0.5)
        self.assertEqual(discount_line.tax_id, dumb_tax)
        self.assertEqual(discount_line.product_uom_qty, 1.0)

        # Two tax groups
        discount_line.unlink()
        solines[0].tax_id = [Command.clear()]
        self.wizard.action_apply_discount()
        discount_lines = self.prescriptions_order.order_line - solines
        self.assertEqual(len(discount_lines), 2)
        self.assertEqual(discount_lines[0].price_unit, -solines[0].price_subtotal * 0.5)
        self.assertEqual(discount_lines[1].price_unit, -solines[1].price_subtotal * 0.5)
        self.assertEqual(discount_lines[0].tax_id, solines[0].tax_id)
        self.assertEqual(discount_lines[1].tax_id, solines[1].tax_id)
        self.assertTrue(all(line.product_uom_qty == 1.0 for line in discount_lines))

    def test_sol_discount(self):
        so_amount = self.prescriptions_order.amount_untaxed
        self.wizard.write({
            'discount_percentage': 0.5,  # 50%
            'discount_type': 'sol_discount',
        })
        self.wizard.action_apply_discount()

        self.assertTrue(
            all(line.discount == 50 for line in self.prescriptions_order.order_line)
        )
        self.assertAlmostEqual(self.prescriptions_order.amount_untaxed, so_amount*0.5)
