

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestNWP(TransactionCase):
    def setUp(self):
        super().setUp()
        self.payor = self.env["res.partner"].create(
            {"name": "Payor", "is_payor": True, "is_pod": True}
        )
        self.coverage_template = self.env["pod.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Coverage"}
        )
        self.company = self.browse_ref("base.main_company")
        self.practice = self.env["res.partner"].create(
            {
                "name": "Practice",
                "is_pod": True,
                "is_practice": True,
                "encounter_sequence_prefix": "S",
                "stock_location_id": self.browse_ref("stock.warehouse0").id,
                "stock_picking_type_id": self.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        self.location = self.env["res.partner"].create(
            {
                "name": "Location",
                "is_pod": True,
                "is_location": True,
                "practice_id": self.practice.id,
                "stock_location_id": self.browse_ref("stock.warehouse0").id,
                "stock_picking_type_id": self.env["stock.picking.type"]
                .search([], limit=1)
                .id,
            }
        )
        self.agreement = self.env["pod.coverage.agreement"].create(
            {
                "name": "Agreement",
                "practice_ids": [(4, self.practice.id)],
                "coverage_template_ids": [(4, self.coverage_template.id)],
                "company_id": self.company.id,
                "authorization_method_id": self.browse_ref(
                    "pod_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "pod_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.patient_01 = self.create_patient("Patient 01")
        self.coverage_01 = self.env["pod.coverage"].create(
            {
                "patient_id": self.patient_01.id,
                "coverage_template_id": self.coverage_template.id,
            }
        )
        self.product_01 = self.create_product("Podiatry resonance")
        self.product_02 = self.create_product("Report")
        self.product_02.pod_commission = True
        self.product_03 = self.env["product.product"].create(
            {
                "type": "service",
                "name": "Clinical material",
                "is_device": False,
                "lst_price": 10.0,
            }
        )

        self.product_04 = self.create_product("MR complex")
        self.plan_definition = self.env["workflow.plan.definition"].create(
            {"name": "Plan", "is_billable": True}
        )

        self.plan_definition2 = self.env["workflow.plan.definition"].create(
            {"name": "Plan2", "is_billable": True}
        )

        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "service_id": self.product_02.id,
                "model_id": self.browse_ref(
                    "pod_clinical_procedure." "model_pod_procedure_request"
                ).id,
            }
        )
        self.activity2 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity2",
                "service_id": self.product_03.id,
                "model_id": self.browse_ref(
                    "pod_clinical_procedure." "model_pod_procedure_request"
                ).id,
            }
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "variable_fee": 0.1,
                "name": "Action",
            }
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity2.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action2",
            }
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "fixed_fee": 10,
                "name": "Action",
            }
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity2.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "name": "Action2",
            }
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity2.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "name": "Action3",
            }
        )
        self.agreement_line = self.env["pod.coverage.agreement.item"].create(
            {
                "product_id": self.product_01.id,
                "coverage_agreement_id": self.agreement.id,
                "plan_definition_id": self.plan_definition.id,
                "total_price": 100,
                "authorization_method_id": self.browse_ref(
                    "pod_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "pod_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.agreement_line2 = self.env["pod.coverage.agreement.item"].create(
            {
                "product_id": self.product_03.id,
                "coverage_agreement_id": self.agreement.id,
                "plan_definition_id": self.plan_definition.id,
                "total_price": 100.0,
                "authorization_method_id": self.browse_ref(
                    "pod_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "pod_financial_coverage_request.format_anything"
                ).id,
            }
        )
        self.agreement_line3 = self.env["pod.coverage.agreement.item"].create(
            {
                "product_id": self.product_04.id,
                "coverage_agreement_id": self.agreement.id,
                "plan_definition_id": self.plan_definition2.id,
                "total_price": 100.0,
                "authorization_method_id": self.browse_ref(
                    "pod_financial_coverage_request.without"
                ).id,
                "authorization_format_id": self.browse_ref(
                    "pod_financial_coverage_request.format_anything"
                ).id,
            }
        )

    def create_patient(self, name):
        return self.env["pod.patient"].create({"name": name})

    def create_product(self, name):
        return self.env["product.product"].create({"type": "service", "name": name})

    def create_practitioner(self, name):
        return self.env["res.partner"].create(
            {
                "name": name,
                "is_practitioner": True,
                "agent_id": True,
                "commission": self.browse_ref("nwp_pod_commission.commission_01").id,
            }
        )

    def create_careplan_and_group(self):
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient_01.id, "practice_id": self.practice.id}
        )
        careplan = self.env["pod.careplan"].create(
            {
                "patient_id": encounter.patient_id.id,
                "practice_id": encounter.practice_id.id,
                "coverage_id": self.coverage_01.id,
            }
        )
        wizard = self.env["pod.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        wizard.run()
        group = self.env["pod.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        group.ensure_one()
        self.assertEqual(group.practice_id, encounter.practice_id)
        return encounter, careplan, group

    def test_change_plan(self):
        self.plan_definition.is_breakdown = False
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group()
        group.refresh()
        requests = group.procedure_request_ids.filtered(
            lambda r: r.fhir_state == "draft"
        )
        self.assertTrue(requests)
        request = requests.filtered(lambda r: r.activity_definition_id == self.activity)
        self.assertTrue(request)
        self.assertEqual(request.variable_fee, 0.1)
        self.assertEqual(request.fixed_fee, 0)
        for child in group.procedure_request_ids:
            child.draft2active()
        self.assertTrue(group.can_change_plan)
        wizard = (
            self.env["pod.request.group.change.plan"]
            .with_context(default_request_group_id=group.id)
            .create({"agreement_line_id": self.agreement_line2.id})
        )
        self.assertIn(self.agreement, wizard.agreement_ids)
        wizard.run()
        with self.assertRaises(ValidationError):
            self.env["pod.request.group.change.plan"].with_context(
                default_request_group_id=group.id
            ).create({"agreement_line_id": self.agreement_line3.id}).run()
