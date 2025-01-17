from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestContactAffiliate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_obj = self.env["res.partner"].with_context(
            test_check_affiliate_practice=True
        )

    def test_practice(self):
        vals = {
            "name": "affiliate",
            "is_affiliate": True,
        }
        with self.assertRaises(ValidationError):
            self.partner_obj.create(vals)
        practice_vals = {
            "name": "test name",
            "is_company": True,
        }
        practice = self.partner_obj.create(practice_vals)
        self.assertTrue(practice.is_company)
        vals["company_id"] = practice.id
        self.assertEqual(practice.affiliate_count, 0)
        affiliate = self.partner_obj.create(vals)
        self.assertTrue(affiliate.is_affiliate)
        self.assertEqual(practice.affiliate_count, 1)
