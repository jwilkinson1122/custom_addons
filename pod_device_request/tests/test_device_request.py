

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestDeviceRequest(TransactionCase):
    def setUp(self):
        super(TestDeviceRequest, self).setUp()
        self.patient = self.browse_ref("pod_base.patient_01")
        stock_location = self.browse_ref("stock.warehouse0").lot_stock_id
        picking_type = self.env["stock.picking.type"].search([], limit=1)
        self.location = self.env["res.partner"].create(
            {
                "name": "Test",
                "is_location": True,
                "stock_location_id": stock_location.id,
                "stock_picking_type_id": picking_type.id,
            }
        )
        self.device = self.env["product.product"].create(
            {"name": "Device", "is_device": True, "type": "consu"}
        )

    def test_flow(self):
        request_obj = self.env["pod.device.request"]
        request = request_obj.new(
            {
                "patient_id": self.patient.id,
                "product_id": self.device.id,
                "qty": 1,
            }
        )
        request.onchange_product_id()
        request = request.create(request._convert_to_write(request._cache))
        request.draft2active()
        self.assertEqual(request.fhir_state, "active")
        res = request.action_view_device_administration()
        self.assertFalse(res["res_id"])
        self.assertEqual(request.device_administration_count, 0)
        event = request.generate_event()
        request.refresh()
        self.assertGreater(request.device_administration_count, 0)
        event.preparation2in_progress()
        self.assertEqual(event.fhir_state, "in-progress")
        event.in_progress2suspended()
        self.assertEqual(event.fhir_state, "suspended")
        event.suspended2in_progress()
        self.assertEqual(event.fhir_state, "in-progress")
        with self.assertRaises(ValidationError):
            event.in_progress2completed()
        event.location_id = self.location
        event.in_progress2completed()
        self.assertEqual(event.fhir_state, "completed")
        self.assertTrue(event.move_ids)
        self.assertTrue(event.occurrence_date)
        res = event.action_view_stock_moves()
        self.assertTrue(res["domain"])
        res = request.action_view_device_administration()
        self.assertEqual(res["res_id"], event.id)
