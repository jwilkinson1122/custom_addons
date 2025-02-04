from odoo_test_helper import FakeModelLoader

from odoo.tests import common


class CommonTestProductSelectionWizard(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .product_selection_wizard_test import ProductSelectionWizardTest

        cls.loader.update_registry((ProductSelectionWizardTest,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super().tearDownClass()
