# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import common, new_test_user


class TestPodiatry(common.TransactionCase):

    def test_manager_create_device(self):
        manager = new_test_user(self.env, "test podiatry manager", groups="podiatry.podiatry_group_manager,base.group_partner_manager")
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        line = self.env["podiatry.device.model.line"].create({
            "name": "Audi",
        })
        model = self.env["podiatry.device.model"].create({
            "line_id": line.id,
            "name": "A3",
        })
        self.env["podiatry.device"].with_user(manager).create({
            "model_id": model.id,
            "patient_id": user.partner_id.id,
            "plan_to_change_device": False
        })
