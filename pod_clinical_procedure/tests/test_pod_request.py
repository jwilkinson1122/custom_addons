from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatryRequest(TransactionCase):
    def setUp(self):
        super(TestPodiatryRequest, self).setUp()
        self.patient = self.env["pod.patient"].create(
            {"name": "Test Patient"}
        )
        self.patient2 = self.env["pod.patient"].create(
            {"name": "Test Patient2"}
        )

    def test_constrains(self):
        request = self.env["pod.procedure.request"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["pod.procedure.request"].create(
                {
                    "patient_id": self.patient2.id,
                    "procedure_request_id": request.id,
                }
            )

    def test_constrains_procedure(self):
        request = self.env["pod.procedure.request"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["pod.procedure"].create(
                {
                    "patient_id": self.patient2.id,
                    "procedure_request_id": request.id,
                }
            )

    def test_views(self):
        # procedure
        procedure = self.env["pod.procedure.request"].create(
            {"patient_id": self.patient.id}
        )
        procedure._compute_procedure_request_ids()
        self.assertEqual(procedure.procedure_request_count, 0)
        procedure.with_context(
            inverse_id="active_id", model_name="pod.procedure.request"
        ).action_view_request()
        # 1 procedure
        procedure2 = self.env["pod.procedure.request"].create(
            {
                "patient_id": self.patient.id,
                "procedure_request_id": procedure.id,
            }
        )
        procedure._compute_procedure_request_ids()
        self.assertEqual(procedure.procedure_request_ids.ids, [procedure2.id])
        self.assertEqual(procedure.procedure_request_count, 1)
        procedure.with_context(
            inverse_id="active_id", model_name="pod.procedure.request"
        ).action_view_request()
        # 2 procedure
        procedure3 = self.env["pod.procedure.request"].create(
            {
                "patient_id": self.patient.id,
                "procedure_request_id": procedure.id,
            }
        )
        procedure._compute_procedure_request_ids()
        self.assertEqual(procedure.procedure_request_count, 2)
        self.assertEqual(
            procedure.procedure_request_ids.ids.sort(),
            [procedure2.id, procedure3.id].sort(),
        )
        procedure.with_context(
            inverse_id="active_id", model_name="pod.procedure.request"
        ).action_view_request()