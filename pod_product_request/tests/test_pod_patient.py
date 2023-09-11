from odoo.tests.common import TransactionCase


class TestPodiatryPatient(TransactionCase):
    def setUp(self):
        super(TestPodiatryPatient, self).setUp()
        self.patient = self.env["pod.patient"].create({"name": "Patient"})
        self.encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.external_product_request_order = self.env[
            "pod.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": self.patient.id,
            }
        )
        self.internal_product_request_order = self.env[
            "pod.product.request.order"
        ].create(
            {
                "category": "inpatient",
                "patient_id": self.patient.id,
            }
        )

    def test_create_pod_product_request(self):
        action = self.patient.with_context(
            {"default_category": "discharge"}
        ).create_pod_product_request_order()
        self.assertEqual(action["res_model"], "pod.product.request.order")
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(action["context"]["default_category"], "discharge")

    def test_action_view_external_pod_product_request_order_ids(self):
        self.assertEqual(self.patient.external_product_request_order_count, 1)
        action = (
            self.patient.action_view_external_pod_product_request_order_ids()
        )
        self.assertEqual(
            action["res_id"], self.external_product_request_order.id
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(action["context"]["default_category"], "discharge")

    def test_action_view_internal_pod_product_request_order_ids(self):
        self.assertEqual(self.patient.internal_product_request_order_count, 1)
        action = (
            self.patient.action_view_internal_pod_product_request_order_ids()
        )
        self.assertEqual(
            action["res_id"], self.internal_product_request_order.id
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(action["context"]["default_category"], "inpatient")
