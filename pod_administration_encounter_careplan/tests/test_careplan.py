from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestEncounter(TransactionCase):
    def setUp(self):
        super(TestEncounter, self).setUp()
        self.patient = self.env["pod.patient"].create({"name": "Patient"})
        self.patient_2 = self.env["pod.patient"].create(
            {"name": "Patient 2"}
        )
        self.plan = self.env["workflow.plan.definition"].create(
            {
                "name": "Knee MR",
                "description": "Basic MR",
                "state": "active",
            }
        )
        self.product = self.env["product.product"].create(
            {"name": "DEMO Product", "type": "service"}
        )
        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "MCT",
                "description": "demo",
                "model_id": self.env.ref(
                    "pod_clinical_careplan.model_pod_careplan"
                ).id,
                "state": "active",
                "service_id": self.product.id,
                "quantity": 1,
            }
        )
        self.action = self.env["workflow.plan.definition.action"].create(
            {
                "name": "Action",
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan.id,
            }
        )

    def test_create_careplan_constrains(self):
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.assertEqual(encounter.careplan_count, 0)
        res = encounter.action_view_careplans()
        self.assertFalse(res.get("res_id"))
        careplan = self.env["pod.careplan"].create(
            {"patient_id": self.patient.id, "encounter_id": encounter.id}
        )
        self.assertEqual(encounter.careplan_count, 1)
        with self.assertRaises(ValidationError):
            careplan.patient_id = self.patient_2

    def test_create_careplan(self):
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.assertEqual(encounter.careplan_count, 0)
        res = encounter.action_view_careplans()
        self.assertFalse(res.get("res_id"))
        careplan = self.env["pod.careplan"].create(
            {"patient_id": self.patient.id, "encounter_id": encounter.id}
        )
        self.assertEqual(encounter.careplan_count, 1)
        res = encounter.action_view_careplans()
        self.assertTrue(res.get("res_id"))
        self.env["pod.careplan"].create(
            {"patient_id": self.patient.id, "encounter_id": encounter.id}
        )
        self.assertEqual(encounter.careplan_count, 2)
        res = encounter.action_view_careplans()
        self.assertFalse(res.get("res_id"))
        self.env["pod.careplan.add.plan.definition"].create(
            {"careplan_id": careplan.id, "plan_definition_id": self.plan.id}
        ).run()
