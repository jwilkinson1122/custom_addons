# -*- coding: utf-8 -*-

from odoo.tests import common, new_test_user


class TestPrescription(common.TransactionCase):

    def test_manager_create_prescription(self):
        manager = new_test_user(self.env, "test prescription manager", groups="prescription.prescription_group_manager,base.group_partner_manager")
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        line = self.env["prescription.type.model.line"].create({
            "name": "Audi",
        })
        model = self.env["prescription.type.model"].create({
            "line_id": line.id,
            "name": "A3",
        })
        self.env["prescription.type"].with_user(manager).create({
            "model_id": model.id,
            "location_id": user.partner_id.id,
            "plan_to_change_prescription": False
        })
