

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatryLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_obj = self.env["res.partner"].with_context(
            test_check_pod_location=True
        )

    def test_location(self):
        vals = {
            "name": "location",
            "is_location": True,
        }
        with self.assertRaises(ValidationError):
            self.partner_obj.create(vals)
        account_vals = {
            "name": "test name",
            "is_company": True,
        }
        account = self.partner_obj.create(account_vals)
        self.assertTrue(account.is_company)
        vals["account_id"] = account.id
        self.assertEqual(account.location_count, 0)
        location = self.partner_obj.create(vals)
        self.assertTrue(location.is_location)
        self.assertEqual(account.location_count, 1)
