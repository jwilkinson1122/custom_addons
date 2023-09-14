

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatryLocation(TransactionCase):
    def test_center(self):
        vals = {
            "name": "reception",
            "is_reception": True,
        }
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(vals)
        center_vals = {
            "name": "test name",
            "is_center": True,
        }
        center = self.env["res.partner"].create(center_vals)
        self.assertTrue(center.is_center)
        self.assertEqual(center.reception_count, 0)
        vals["center_id"] = center.id
        location = self.env["res.partner"].create(vals)
        self.assertTrue(location.is_reception)
        self.assertEqual(center.reception_count, 1)
        self.assertEqual(center.location_count, 0)
        self.env["res.partner"].create(
            {"name": "Location", "is_location": True, "center_id": center.id}
        )
        self.assertEqual(center.reception_count, 1)
        self.assertEqual(center.location_count, 1)
