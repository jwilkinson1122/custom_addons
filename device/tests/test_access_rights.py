# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import common, new_test_user


class TestDevice(common.TransactionCase):

    def test_manager_create_custom(self):
        manager = new_test_user(self.env, "test device manager", groups="device.device_group_manager,base.group_partner_manager")
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["device.custom.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["device.custom.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        self.env["device.custom"].with_user(manager).create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_orthotic": False
        })
