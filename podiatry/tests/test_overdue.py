# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import common, new_test_user
from odoo import fields


class TestPodiatry(common.TransactionCase):

    def test_search_renewal(self):
        """
            Should find the device with overdue prescription or renewal due soon
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        line = self.env["podiatry.device.model.line"].create({
            "name": "Audi",
        })
        model = self.env["podiatry.device.model"].create({
            "line_id": line.id,
            "name": "A3",
        })
        device_1 = self.env["podiatry.device"].create({
            "model_id": model.id,
            "patient_id": user.partner_id.id,
            "plan_to_change_device": False
        })

        device_2 = self.env["podiatry.device"].create({
            "model_id": model.id,
            "patient_id": user.partner_id.id,
            "plan_to_change_device": False
        })
        Log = self.env['podiatry.device.log.prescription']
        log = Log.create({
            'device_id': device_2.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=10)
        })
        res = self.env["podiatry.device"].search([('prescription_renewal', '=', True), ('id', '=', device_2.id)])
        self.assertEqual(res, device_2)

        log = Log.create({
            'device_id': device_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-10)
        })
        res = self.env["podiatry.device"].search([('prescription_renewal_overdue', '=', True), ('id', '=', device_1.id)])
        self.assertEqual(res, device_1)
