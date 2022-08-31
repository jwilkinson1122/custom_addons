

from odoo.tests.common import TransactionCase


class TestPodiatryLocation(TransactionCase):
    def test_location(self):
        location_vals = {
            "name": "test name",
            "description": "test description",
            "is_location": True,
        }
        location = self.env["res.partner"].create(location_vals)
        self.assertTrue(location.is_location)
