from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPractitionerCondition(TransactionCase):
    def test_condition(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_pod": True,
                "is_practitioner": True,
            }
        )
        service = self.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )
        self.env["pod.practitioner.condition"].create(
            {"practitioner_id": practitioner.id}
        )
        self.env["pod.practitioner.condition"].create(
            {"practitioner_id": practitioner.id, "service_id": service.id}
        )
        self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "procedure_service_id": service.id,
            }
        )
        self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "service_id": service.id,
                "procedure_service_id": service.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.practitioner.condition"].create(
                {
                    "practitioner_id": practitioner.id,
                    "procedure_service_id": service.id,
                }
            )

    def test_condition_archived(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_pod": True,
                "is_practitioner": True,
            }
        )
        service = self.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )
        self.env["pod.practitioner.condition"].create(
            {"practitioner_id": practitioner.id}
        )
        self.env["pod.practitioner.condition"].create(
            {"practitioner_id": practitioner.id, "service_id": service.id}
        )
        condition = self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "procedure_service_id": service.id,
            }
        )
        self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "service_id": service.id,
                "procedure_service_id": service.id,
            }
        )
        condition.toggle_active()
        self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "procedure_service_id": service.id,
            }
        )

    def test_condition_practice_1(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_pod": True,
                "is_practitioner": True,
            }
        )
        practice_01 = self.env["res.partner"].create(
            {"name": "Practitioner", "is_pod": True, "is_company": True}
        )
        practice_02 = self.env["res.partner"].create(
            {"name": "Practitioner", "is_pod": True, "is_company": True}
        )
        self.env["pod.practitioner.condition"].create(
            {"practitioner_id": practitioner.id}
        )
        self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "practice_ids": [(4, practice_01.id), (4, practice_02.id)],
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.practitioner.condition"].create(
                {
                    "practitioner_id": practitioner.id,
                    "practice_ids": [(4, practice_01.id)],
                }
            )

    def test_condition_practice_2(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_pod": True,
                "is_practitioner": True,
            }
        )
        practice_01 = self.env["res.partner"].create(
            {"name": "Practitioner", "is_pod": True, "is_company": True}
        )
        practice_02 = self.env["res.partner"].create(
            {"name": "Practitioner", "is_pod": True, "is_company": True}
        )
        self.env["pod.practitioner.condition"].create(
            {"practitioner_id": practitioner.id}
        )
        self.env["pod.practitioner.condition"].create(
            {
                "practitioner_id": practitioner.id,
                "practice_ids": [(4, practice_01.id)],
            }
        )
        with self.assertRaises(ValidationError):
            self.env["pod.practitioner.condition"].create(
                {
                    "practitioner_id": practitioner.id,
                    "practice_ids": [(4, practice_01.id), (4, practice_02.id)],
                }
            )
