
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPrescription(TransactionCase):
    def setUp(self):
        super(TestPrescription, self).setUp()
        self.product_obj = self.env["product.template"]
        self.code_obj = self.env["code.concept"]
        self.code = self.code_obj.search(
            [("is_medical_device_code", "=", True)], limit=1
        )
        self.code_obj = self.env["code.concept"]
        self.form = self.code_obj.search(
            [("is_prescription_form", "=", True)], limit=1
        )
        self.vals = {
            "name": "Name",
            "type": "consu",
            "is_medical_device": True,
            "form_id": self.form.id,
            "code_id": self.code.id,
        }

    def test_codification(self):
        product = self.product_obj.create(self.vals)
        self.assertTrue(product.is_medical_device)

    def test_constrains(self):
        self.vals["type"] = "service"
        with self.assertRaises(ValidationError):
            self.product_obj.create(self.vals)
