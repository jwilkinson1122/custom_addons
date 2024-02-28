# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import common, new_test_user
from odoo import fields


class TestDevice(common.TransactionCase):

    def test_search_renewal(self):
        """
            Should find the car with overdue contract or renewal due soon
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["device.custom.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["device.custom.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        car_1 = self.env["device.custom"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_orthotic": False
        })

        car_2 = self.env["device.custom"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_orthotic": False
        })
        Log = self.env['device.custom.log.contract']
        Log.create({
            'custom_id': car_2.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=10)
        })
        res = self.env["device.custom"].search([('contract_renewal_due_soon', '=', True), ('id', '=', car_2.id)])
        self.assertEqual(res, car_2)

        Log.create({
            'custom_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-10)
        })
        res = self.env["device.custom"].search([('contract_renewal_overdue', '=', True), ('id', '=', car_1.id)])
        self.assertEqual(res, car_1)
