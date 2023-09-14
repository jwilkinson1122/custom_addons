from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestClinicalLaboratory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["pod.patient"].create({"name": "Patient"})
        self.patient2 = self.env["pod.patient"].create({"name": "Test Patient2"})

    def test_constrains(self):
        request = self.env["pod.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["pod.laboratory.request"].create(
                {
                    "patient_id": self.patient2.id,
                    "laboratory_request_id": request.id,
                }
            )

    def test_constrains_event(self):
        request = self.env["pod.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["pod.laboratory.event"].create(
                {
                    "patient_id": self.patient2.id,
                    "laboratory_request_id": request.id,
                }
            )

    def test_laboratory(self):
        request = self.env["pod.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        self.assertEqual(request.laboratory_event_count, 0)
        self.assertEqual(request.laboratory_request_count, 0)
        event = request.generate_event()
        self.assertEqual(request.laboratory_event_count, 1)
        self.assertEqual(event.id, request.action_view_laboratory_events()["res_id"])
        request.action_view_request_parameters()
