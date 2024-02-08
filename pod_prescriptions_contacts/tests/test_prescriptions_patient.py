from odoo import fields
from odoo.tests import TransactionCase


class TestPrescriptionsPatient(TransactionCase):
    def test_creation(self):
        patient = self.env["prescriptions.patient"].create({"name": "Test Patient"})
        self.assertTrue(patient.internal_identifier)
        self.assertNotEqual(patient.internal_identifier, "/")
        patient.birth_date = fields.Date.today()

