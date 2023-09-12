from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPrescription(TransactionCase):
    def setUp(self):
        super(TestPrescription, self).setUp()
        self.product_obj = self.env["product.template"]
        self.sct_obj = self.env["pod.sct.concept"]
        self.sct_code = self.sct_obj.search(
            [("is_prescription_code", "=", True)], limit=1
        )
        self.sct_obj = self.env["pod.sct.concept"]
        self.atc_code = self.env["pod.atc.concept"].search(
            [("parent_id", "!=", False)], limit=1
        )
        self.form = self.sct_obj.search(
            [("is_prescription_form", "=", True)], limit=1
        )
        self.vals = {
            "name": "Name",
            "type": "consu",
            "is_prescription": True,
            "form_id": self.form.id,
            "sct_code_id": self.sct_code.id,
            "atc_code_id": self.atc_code.id,
        }

    def test_classification(self):
        product = self.product_obj.create(self.vals)
        self.assertTrue(product.is_prescription)

    def test_constrains(self):
        self.vals["type"] = "service"
        with self.assertRaises(ValidationError):
            self.product_obj.create(self.vals)
