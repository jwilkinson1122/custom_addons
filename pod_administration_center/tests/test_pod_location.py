
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatryLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_obj = self.env["res.partner"].with_context(
            test_check_location_center=True
        )

    def test_center(self):
        vals = {
            "name": "location",
            "is_location": True,
        }
        with self.assertRaises(ValidationError):
            self.partner_obj.create(vals)
        center_vals = {
            "name": "test name",
            "is_center": True,
        }
        center = self.partner_obj.create(center_vals)
        self.assertTrue(center.is_center)
        vals["center_id"] = center.id
        self.assertEqual(center.location_count, 0)
        location = self.partner_obj.create(vals)
        self.assertTrue(location.is_location)
        self.assertEqual(center.location_count, 1)
