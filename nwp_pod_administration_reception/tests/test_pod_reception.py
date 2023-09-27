

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatryLocation(TransactionCase):
    def test_practice(self):
        vals = {
            "name": "reception",
            "is_reception": True,
        }
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(vals)
        practice_vals = {
            "name": "test name",
            "is_company": True,
        }
        practice = self.env["res.partner"].create(practice_vals)
        self.assertTrue(practice.is_company)
        self.assertEqual(practice.reception_count, 0)
        vals["practice_id"] = practice.id
        location = self.env["res.partner"].create(vals)
        self.assertTrue(location.is_reception)
        self.assertEqual(practice.reception_count, 1)
        self.assertEqual(practice.location_count, 0)
        self.env["res.partner"].create(
            {"name": "Location", "is_location": True, "practice_id": practice.id}
        )
        self.assertEqual(practice.reception_count, 1)
        self.assertEqual(practice.location_count, 1)
