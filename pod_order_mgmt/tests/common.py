from odoo_test_helper import FakeModelLoader

from odoo.tests import common


class CommonTestMultiStepWizard(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .multi_step_wizard_test import MultiStepWizardTest

        cls.loader.update_registry((MultiStepWizardTest,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super().tearDownClass()
