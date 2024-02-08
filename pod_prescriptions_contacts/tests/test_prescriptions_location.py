

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPrescriptionsLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_obj = self.env["res.partner"].with_context(
            test_check_location_practice=True
        )

    def test_practice(self):
        vals = {
            "name": "location",
            "is_location": True,
        }
        with self.assertRaises(ValidationError):
            self.partner_obj.create(vals)
        practice_vals = {
            "name": "test name",
            "is_company": True,
        }
        practice = self.partner_obj.create(practice_vals)
        self.assertTrue(practice.is_company)
        vals["practice_id"] = practice.id
        self.assertEqual(practice.location_count, 0)
        location = self.partner_obj.create(vals)
        self.assertTrue(location.is_location)
        self.assertEqual(practice.location_count, 1)
