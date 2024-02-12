# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import AccessError
from odoo.addons.sale_prescription.tests.common import TestCommonSalePrescriptionNoChart
from odoo.tests import tagged


@tagged('-at_install', 'post_install')
class TestAccessRights(TestCommonSalePrescriptionNoChart):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # Create a users
        group_sale_user = cls.env.ref('sales_team.group_sale_salesman')
        group_prescription_user = cls.env.ref('prescription.group_prescription_user')
        cls.user_salesperson = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Le Grand Jojo User',
            'login': 'grand.jojo',
            'email': 'grand.jojo@chansonbelge.com',
            'groups_id': [(6, 0, [group_sale_user.id])]
        })
        cls.user_prescriptionperson = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Jean-Luc Fonck',
            'login': 'jl.fonck',
            'email': 'jl.fonck@chansonbelge.com',
            'groups_id': [(6, 0, [group_prescription_user.id])]
        })

    def test_access_saleperson(self):
        """ Check a saleperson (only) can generate a PO and a PO user can not confirm a SO """
        SaleOrder = self.env['sale.order'].with_context(tracking_disable=True)

        sale_order = SaleOrder.with_user(self.user_salesperson).create({
            'partner_id': self.partner_a.id,
            'user_id': self.user_salesperson.id
        })

        sol_service_prescription = self.env['sale.order.line'].with_user(self.user_salesperson).create({
            'product_id': self.service_prescription_1.id,
            'product_uom_qty': 4,
            'order_id': sale_order.id,
            'tax_id': False,
        })

        # confirming SO will create the PO even if you don't have the rights
        sale_order.action_confirm()
        sale_order._action_cancel()

        self.assertTrue(sale_order.name, "Saleperson can read its own SO")

        action = sale_order.sudo().action_view_prescriptions()

        # try to access PO as sale person
        with self.assertRaises(AccessError):
            prescriptions = self.env['prescription'].with_user(self.user_salesperson).browse(action['res_id'])
            prescriptions.read()

        # try to access PO as prescription person
        prescriptions = self.env['prescription'].with_user(self.user_prescriptionperson).browse(action['res_id'])
        prescriptions.read()

        # try to access the PO lines from the SO, as sale person
        with self.assertRaises(AccessError):
            sol_service_prescription.with_user(self.user_salesperson).prescription_line_ids.read()
