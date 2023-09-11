from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPrescriptionRequest(TransactionCase):
    def setUp(self):
        super(TestPrescriptionRequest, self).setUp()
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
        self.prescription = self.env["product.product"].create(
            {"name": "Prescription", "is_prescription": True, "type": "consu"}
        )

    def test_flow(self):
        request_obj = self.env["pod.prescription.request"]
        request = request_obj.new(
            {
                "patient_id": self.patient.id,
                "product_id": self.prescription.id,
                "qty": 1,
            }
        )
        request.onchange_product_id()
        request = request.create(request._convert_to_write(request._cache))
        request.draft2active()
        self.assertEqual(request.fhir_state, "active")
        res = request.action_view_prescription_administration()
        self.assertFalse(res["res_id"])
        self.assertEqual(request.prescription_administration_count, 0)
        event = request.generate_event()
        request.refresh()
        self.assertGreater(request.prescription_administration_count, 0)
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
        res = request.action_view_prescription_administration()
        self.assertEqual(res["res_id"], event.id)
