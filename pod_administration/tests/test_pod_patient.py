
from odoo import fields
from odoo.tests import TransactionCase


class TestPodPatient(TransactionCase):
    def test_creation(self):
        patient = self.env["pod.patient"].create({"name": "Test Patient"})
        self.assertTrue(patient.internal_identifier)
        self.assertNotEqual(patient.internal_identifier, "/")
        patient.birth_date = fields.Date.today()
        patient.deceased_date = fields.Date.today()
        self.assertTrue(patient.is_deceased)
