# -*- coding: utf-8 -*-

from odoo.tests import common, new_test_user
from odoo import fields


class TestPrescription(common.TransactionCase):

    def test_search_renewal(self):
        """
            Should find the car with overdue prescription or renewal due soon
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        line = self.env["prescription.type.model.line"].create({
            "name": "Audi",
        })
        model = self.env["prescription.type.model"].create({
            "line_id": line.id,
            "name": "A3",
        })
        car_1 = self.env["prescription.type"].create({
            "model_id": model.id,
            "location_id": user.partner_id.id,
            "plan_to_change_prescription": False
        })

        car_2 = self.env["prescription.type"].create({
            "model_id": model.id,
            "location_id": user.partner_id.id,
            "plan_to_change_prescription": False
        })
        Log = self.env['prescription.type.log']
        Log.create({
            'prescription_id': car_2.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=10)
        })
        res = self.env["prescription.type"].search([('prescription_renewal_due_soon', '=', True), ('id', '=', car_2.id)])
        self.assertEqual(res, car_2)

        Log.create({
            'prescription_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-10)
        })
        res = self.env["prescription.type"].search([('prescription_renewal_overdue', '=', True), ('id', '=', car_1.id)])
        self.assertEqual(res, car_1)
