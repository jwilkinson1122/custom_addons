

from odoo.tests.common import TransactionCase


class TestLaboratoryService(TransactionCase):
    def setUp(self):
        super().setUp()
        self.lab_service = self.env["pod.laboratory.service"].create(
            {
                "code": "INTERNAL_CODE",
                "name": "name",
                "laboratory_code": "LAB_CODE",
                "service_price_ids": [
                    (0, 0, {"laboratory_code": "1", "amount": 10, "cost": 5})
                ],
            }
        )

    def test_search(self):
        self.assertIn(
            self.lab_service,
            self.env["pod.laboratory.service"].search(
                [("name", "=", "INTERNAL_CODE")]
            ),
        )
        res = [
            s[0]
            for s in self.env["pod.laboratory.service"].name_search("INTERNAL_CODE")
        ]
        self.assertIn(self.lab_service.id, res)
        self.assertEqual(self.lab_service.display_name, "[INTERNAL_CODE] name")
