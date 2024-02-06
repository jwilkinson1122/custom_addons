# -*- coding: utf-8 -*-


from odoo.tests import HttpCase, tagged, Form
from odoo.addons.prescription.tests.common import TestPrescriptionCommon
from odoo.addons.mail.tests.common import mail_new_test_user


@tagged('post_install', '-at_install')
class TestControllersAccessRights(HttpCase, TestPrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = mail_new_test_user(cls.env, login='jimmy-portal', groups='base.group_portal')

    def test_RX_and_DO_portal_acess(self):
        """ Ensure that it is possible to open both RX and DO, either using the access token
        or being connected as portal user"""
        rx_form = Form(self.env['prescription.order'])
        rx_form.partner_id = self.portal_user.partner_id
        with rx_form.order_line.new() as line:
            line.product_id = self.product_a
        rx = rx_form.save()
        rx.action_confirm()
        picking = rx.picking_ids

        # Try to open RX/DO using the access token or being connected as portal user
        for login in (None, self.portal_user.login):
            rx_url = '/my/prescriptions/%s' % rx.id
            picking_url = '/my/picking/pdf/%s' % picking.id

            self.authenticate(login, login)

            if not login:
                rx._portal_ensure_token()
                rx_token = rx.access_token
                rx_url = '%s?access_token=%s' % (rx_url, rx_token)
                picking_url = '%s?access_token=%s' % (picking_url, rx_token)

            response = self.url_open(
                url=rx_url,
                allow_redirects=False,
            )
            self.assertEqual(response.status_code, 200, 'Should be correct %s' % ('with a connected user' if login else 'using access token'))
            response = self.url_open(
                url=picking_url,
                allow_redirects=False,
            )
            self.assertEqual(response.status_code, 200, 'Should be correct %s' % ('with a connected user' if login else 'using access token'))
