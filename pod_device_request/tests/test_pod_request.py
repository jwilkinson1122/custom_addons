

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
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.device = self.env["product.product"].create(
            {"name": "Device", "is_device": True, "type": "consu"}
        )

    def test_constrains(self):
        request = self.env["pod.device.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.device.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.device.request"].create(
                {
                    "patient_id": self.patient2.id,
                    "device_request_id": request.id,
                    "product_id": self.device.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty": 1,
                }
            )

    def test_constrains_administration(self):
        request = self.env["pod.device.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.device.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.device.administration"].create(
                {
                    "patient_id": self.patient2.id,
                    "device_request_id": request.id,
                    "product_id": self.device.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty": 1,
                }
            )

    def test_views(self):
        # device request
        device_request = self.env["pod.device.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.device.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        device_request._compute_device_request_ids()
        self.assertEqual(device_request.device_request_count, 0)
        device_request.with_context(
            inverse_id="active_id", model_name="pod.device.request"
        ).action_view_request()
        # 1 device request
        device_request2 = self.env["pod.device.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.device.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
                "device_request_id": device_request.id,
            }
        )
        device_request._compute_device_request_ids()
        self.assertEqual(
            device_request.device_request_ids.ids,
            [device_request2.id],
        )
        self.assertEqual(device_request.device_request_count, 1)
        device_request.with_context(
            inverse_id="active_id", model_name="pod.device.request"
        ).action_view_request()
        # 2 device request
        device_request3 = self.env["pod.device.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.device.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
                "device_request_id": device_request.id,
            }
        )
        device_request._compute_device_request_ids()
        self.assertEqual(device_request.device_request_count, 2)
        self.assertEqual(
            device_request.device_request_ids.ids.sort(),
            [device_request2.id, device_request3.id].sort(),
        )
        device_request.with_context(
            inverse_id="active_id", model_name="pod.device.request"
        ).action_view_request()
