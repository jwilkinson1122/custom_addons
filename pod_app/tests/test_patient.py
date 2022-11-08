from odoo.tests.common import TransactionCase


class TestPatient(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.Patient = self.env["pod.patient"]
        self.patient1 = self.Patient.create({
            "name": "Odoo Development Essentials",
            "isbn": "879-1-78439-279-6"})

    def test_patient_create(self):
        "New Patients are active by default"
        self.assertEqual(
            self.patient1.active, True
        )

    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.patient1._check_isbn)
