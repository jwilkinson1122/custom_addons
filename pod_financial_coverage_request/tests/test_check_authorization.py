

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
        self.format = self.env["pod.authorization.format"].create(
            {
                "name": "Number",
                "code": "testing_number",
                "always_authorized": False,
                "authorization_format": "^[0-9]*$",
            }
        )
        self.method = self.browse_ref("pod_financial_coverage_request.only_number")
        self.agreement = self.env["pod.coverage.agreement"].create(
            {
                "name": "Agreement",
                "practice_ids": [(4, self.practice.id)],
                "coverage_template_ids": [(4, self.coverage_template.id)],
                "company_id": self.company.id,
                "authorization_method_id": self.method.id,
                "authorization_format_id": self.format.id,
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
        self.plan_definition = self.env["workflow.plan.definition"].create(
            {"name": "Plan", "is_billable": True}
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
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity.id,
                "direct_plan_definition_id": self.plan_definition.id,
                "is_billable": False,
                "name": "Action",
            }
        )
        self.agreement_line = self.env["pod.coverage.agreement.item"].create(
            {
                "product_id": self.product_01.id,
                "coverage_agreement_id": self.agreement.id,
                "plan_definition_id": self.plan_definition.id,
                "total_price": 100,
                "authorization_method_id": self.browse_ref(
                    "pod_financial_coverage_request.only_number"
                ).id,
                "authorization_format_id": self.format.id,
            }
        )

    def create_patient(self, name):
        return self.env["pod.patient"].create({"name": name})

    def create_product(self, name):
        return self.env["product.product"].create({"type": "service", "name": name})

    def create_practitioner(self, name):
        return self.env["res.partner"].create(
            {"name": name, "is_practitioner": True, "agent": True}
        )

    def create_careplan_and_group(self, number=False):
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
                "authorization_number": number,
            }
        )
        wizard.run()
        group = self.env["pod.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        group.ensure_one()
        self.assertEqual(group.practice_id, encounter.practice_id)
        return encounter, careplan, group

    def test_check_authorization(self):
        self.plan_definition.is_breakdown = False
        self.plan_definition.is_billable = True
        number = "AAA"
        encounter, careplan, group = self.create_careplan_and_group(number)
        self.assertEqual(group.authorization_status, "pending")
        self.env["pod.request.group.check.authorization"].with_context(
            default_request_group_id=group.id
        ).create({"authorization_number": "1234"}).run()
        group.refresh()
        self.assertEqual(group.authorization_status, "authorized")
        wizard = (
            self.env["pod.request.group.check.authorization"]
            .with_context(default_request_group_id=group.id)
            .create({"authorization_number": "1234a"})
        )
        self.assertEqual(wizard.authorization_method_id, self.method)
        self.assertEqual(wizard.authorization_method_ids, self.method)
        wizard.run()
        group.refresh()
        self.assertEqual(group.authorization_status, "pending")

    def test_check_authorization_without(self):
        self.plan_definition.is_breakdown = False
        self.plan_definition.is_billable = True
        self.agreement_line.write(
            {
                "authorization_method_id": self.browse_ref(
                    "pod_financial_coverage_request.without"
                ).id
            }
        )
        number = "AAA"
        encounter, careplan, group = self.create_careplan_and_group(number)
        self.assertEqual(group.authorization_status, "authorized")

    def test_check_authorization_correct(self):
        self.plan_definition.is_breakdown = False
        self.plan_definition.is_billable = True
        number = "1234"
        encounter, careplan, group = self.create_careplan_and_group(number)
        self.assertEqual(group.authorization_status, "authorized")
