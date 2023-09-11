from odoo.tests import TransactionCase


class TestClassification(TransactionCase):
    def setUp(self):
        super(TestClassification, self).setUp()
        self.atc_code = self.env["pod.atc.concept"].search(
            [("parent_id", "!=", False)], limit=1
        )

    def test_atc_code(self):
        code = self.atc_code.code
        self.atc_code.level_code = self.atc_code.level_code + "B"
        self.assertEqual(self.atc_code.code, code + "B")