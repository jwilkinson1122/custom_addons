from odoo.tests.common import tagged

from .common import CommonTestProductSelectionWizard


@tagged("post_install", "-at_install")
class TestProductSelectionWizard(CommonTestProductSelectionWizard):
    def setUp(self):
        super().setUp()
        self.ProductSelectionWizard = self.env["product.selection.wizard.test"]

    def test_behavior(self):
        wizard = self.ProductSelectionWizard.create({})
        wizard.open_next()
        self.assertEqual(wizard.state, "final")
        with self.assertRaises(NotImplementedError):
            wizard.open_next()
        self.assertTrue(wizard.allow_back)
        wizard.open_previous()
        self.assertEqual(wizard.state, "start")
