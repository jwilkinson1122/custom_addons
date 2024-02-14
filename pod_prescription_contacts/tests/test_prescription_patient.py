from odoo import fields
from odoo.tests import TransactionCase


class TestPrescriptionPatient(TransactionCase):
    def test_creation(self):
        patient = self.env["prescription.patient"].create({"name": "Test Patient"})
        self.assertTrue(patient.internal_identifier)
        self.assertNotEqual(patient.internal_identifier, "/")
        patient.birth_date = fields.Date.today()

