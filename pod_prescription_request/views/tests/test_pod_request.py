
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodRequest(TransactionCase):
    def setUp(self):
        super(TestPodRequest, self).setUp()
        self.patient = self.env["pod.patient"].create(
            {"name": "Test Patient"}
        )
        self.patient2 = self.env["pod.patient"].create(
            {"name": "Test Patient2"}
        )
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.prescription = self.env["product.product"].create(
            {"name": "Prescription", "is_medical_device": True, "type": "consu"}
        )

    def test_constrains(self):
        request = self.env["pod.prescription.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.prescription.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.prescription.request"].create(
                {
                    "patient_id": self.patient2.id,
                    "prescription_request_id": request.id,
                    "product_id": self.prescription.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty": 1,
                }
            )

    def test_constrains_administration(self):
        request = self.env["pod.prescription.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.prescription.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.prescription.administration"].create(
                {
                    "patient_id": self.patient2.id,
                    "prescription_request_id": request.id,
                    "product_id": self.prescription.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty": 1,
                }
            )

    def test_views(self):
        # prescription request
        prescription_request = self.env["pod.prescription.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.prescription.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        prescription_request._compute_prescription_request_ids()
        self.assertEqual(prescription_request.prescription_request_count, 0)
        prescription_request.with_context(
            inverse_id="active_id", model_name="pod.prescription.request"
        ).action_view_request()
        # 1 prescription request
        prescription_request2 = self.env["pod.prescription.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.prescription.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
                "prescription_request_id": prescription_request.id,
            }
        )
        prescription_request._compute_prescription_request_ids()
        self.assertEqual(
            prescription_request.prescription_request_ids.ids,
            [prescription_request2.id],
        )
        self.assertEqual(prescription_request.prescription_request_count, 1)
        prescription_request.with_context(
            inverse_id="active_id", model_name="pod.prescription.request"
        ).action_view_request()
        # 2 prescription request
        prescription_request3 = self.env["pod.prescription.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.prescription.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
                "prescription_request_id": prescription_request.id,
            }
        )
        prescription_request._compute_prescription_request_ids()
        self.assertEqual(prescription_request.prescription_request_count, 2)
        self.assertEqual(
            prescription_request.prescription_request_ids.ids.sort(),
            [prescription_request2.id, prescription_request3.id].sort(),
        )
        prescription_request.with_context(
            inverse_id="active_id", model_name="pod.prescription.request"
        ).action_view_request()
