from odoo.tests.common import TransactionCase


class TestPrescription(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.Prescription = self.env["podiatry.prescription"]
        self.prescription1 = self.Prescription.create({
            "name": "Odoo Development Essentials",
            "isbn": "879-1-78439-279-6"})

    def test_prescription_create(self):
        "New Prescriptions are active by default"
        self.assertEqual(
            self.prescription1.active, True
        )

    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.prescription1._check_isbn)
