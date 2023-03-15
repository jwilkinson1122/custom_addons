
from odoo import fields
from odoo.tests import TransactionCase


class TestPodiatryPatient(TransactionCase):
    def test_creation(self):
        patient = self.env["podiatry.patient"].create({"name": "Test Patient"})
        self.assertTrue(patient.internal_identifier)
        self.assertNotEqual(patient.internal_identifier, "ID")
        patient.birth_date = fields.Date.today()
