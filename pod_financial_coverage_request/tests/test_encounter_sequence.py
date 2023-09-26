

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCoverage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["pod.patient"].create({"name": "Patient"})

    def test_write_sequence(self):
        practice = self.env["res.partner"].create({"name": "Practice", "is_practice": True})
        self.assertFalse(practice.encounter_sequence_id)
        with self.assertRaises(ValidationError):
            self.env["pod.encounter"].create(
                {"patient_id": self.patient.id, "practice_id": practice.id}
            )
        practice.write({"encounter_sequence_prefix": "R"})
        self.assertEqual(practice.encounter_sequence_id.prefix, "R")
        self.assertTrue(practice.encounter_sequence_id)
        code = practice.encounter_sequence_id.get_next_char(
            practice.encounter_sequence_id.number_next_actual
        )
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id, "practice_id": practice.id}
        )
        self.assertEqual(encounter.internal_identifier, code)

    def test_create_sequence(self):
        practice = self.env["res.partner"].create(
            {
                "name": "Practice",
                "is_practice": True,
                "encounter_sequence_prefix": "S",
            }
        )
        self.assertTrue(practice.encounter_sequence_id)
        self.assertEqual(practice.encounter_sequence_id.prefix, "S")
        current = practice.encounter_sequence_id.number_next_actual
        code = practice.encounter_sequence_id.get_next_char(current)
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id, "practice_id": practice.id}
        )
        self.assertEqual(encounter.internal_identifier, code)
        practice.write({"encounter_sequence_prefix": "R"})
        self.assertEqual(practice.encounter_sequence_id.prefix, "R")
        self.assertTrue(practice.encounter_sequence_id)
        code = practice.encounter_sequence_id.get_next_char(current + 1)
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id, "practice_id": practice.id}
        )
        self.assertEqual(encounter.internal_identifier, code)
