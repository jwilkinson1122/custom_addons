import logging
import os
import csv
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestCRMImport(TransactionCase):

    def setUp(self):
        """Set up the test environment before each test."""
        super(TestCRMImport, self).setUp()
        self.import_model = self.env["crm.account.import"]

    def test_import_parent_accounts(self):
        """Test importing Parent Accounts from CSV."""
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "crm_active_parent_accounts.csv"
        )
        _logger.info("Starting test: Import Parent Accounts")

        # Run the import
        self.import_model.import_parent_accounts(file_path)

        # Validate that some parent accounts were created
        parent_count = self.env["res.partner"].search_count([("is_account", "=", True)])
        _logger.info(f" Imported {parent_count} parent accounts")

        self.assertGreater(parent_count, 0, "No parent accounts were imported.")

    def test_import_child_accounts(self):
        """Test importing Child Accounts and linking to Parent Accounts."""
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "crm_active_child_accounts.csv"
        )
        _logger.info("Starting test: Import Child Accounts")

        # Run the import
        self.import_model.import_child_accounts(file_path)

        # Validate that some child accounts were created
        child_count = self.env["res.partner"].search_count(
            [("is_affiliate", "=", True)]
        )
        _logger.info(f" Imported {child_count} child accounts")

        self.assertGreater(child_count, 0, "No child accounts were imported.")

    def test_parent_child_linking(self):
        """Test if child accounts are correctly linked to parent accounts."""
        _logger.info("Starting test: Parent-Child Linking")

        # Find a child account with a linked parent
        child = self.env["res.partner"].search(
            [("is_affiliate", "=", True), ("parent_id", "!=", False)], limit=1
        )

        self.assertTrue(child, "No child accounts are linked to parent accounts.")
        _logger.info(
            f" Child Account '{child.name}' is correctly linked to Parent '{child.parent_id.name}'"
        )

    def test_missing_parents(self):
        """Test if child accounts without a parent are handled correctly."""
        _logger.info("Starting test: Handling Missing Parent Accounts")

        # Find child accounts without a parent
        unlinked_children = self.env["res.partner"].search(
            [("is_affiliate", "=", True), ("parent_id", "=", False)]
        )

        self.assertEqual(
            len(unlinked_children), 0, "Some child accounts are missing parent links."
        )
        _logger.info(" All child accounts are correctly linked to parents.")

    def tearDown(self):
        """Clean up after each test."""
        _logger.info("Cleaning up test records.")
        self.env["res.partner"].search([("is_account", "=", True)]).unlink()
        self.env["res.partner"].search([("is_affiliate", "=", True)]).unlink()


# How to Run the Test Script
# 1.	Save the script as test_crm_import.py inside your Odoo custom module folder.
# 2.	Run the test in Odoo's shell mode: odoo-bin shell -c /path/to/odoo.conf
# odoo-bin --test-enable -i your_module_name
# odoo-bin --test-enable -i sync_from_mssql
# Replace your_module_name with your actual module name (e.g., pod_partner_hierarchy).
