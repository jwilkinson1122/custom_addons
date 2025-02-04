# Copyright 2024 Sygel Technology - Alberto Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestPartnerPatient(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]
        self.company = self.partner_model.create(
            {"name": "Test Company", "company_type": "company"}
        )
        self.patient = self.partner_model.create(
            {
                "name": "Test Patient",
                "company_type": "company",
                "parent_id": self.company.id,
            }
        )

    def test_partner_patient_access_link(self):
        res = self.patient.open_patient_form()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "res.partner")
        self.assertEqual(res["res_id"], self.patient.id)
        self.assertEqual(res["view_mode"], "form")
        self.assertEqual(res["target"], "current")
