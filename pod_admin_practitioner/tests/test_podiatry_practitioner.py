

from odoo.tests.common import TransactionCase


class TestPodiatryAdministrationPractitioner(TransactionCase):
    def setUp(self):
        super(TestPodiatryAdministrationPractitioner, self).setUp()
        self.practitioner_model = self.env["res.partner"]
        self.role_model = self.env["podiatry.role"]

    def test_security(self):
        role_vals = {"name": "Nurse", "description": "Nurse"}
        role_1 = self.role_model.create(role_vals)
        practitioner_vals = {
            "is_practitioner": True,
            "name": "Nurse X",
            "practitioner_role_ids": [(6, 0, role_1.ids)],
        }
        practitioner_1 = self.practitioner_model.create(practitioner_vals)
        self.assertNotEquals(practitioner_1, False)
        self.assertNotEquals(practitioner_1.practitioner_role_ids, False)
