# -*- coding: utf-8 -*-

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseUsersCommon, HttpCaseWithUserPortal
from odoo.addons.pod_prescription.tests.common import PrescriptionCommon


@tagged('post_install', '-at_install')
class TestAccessRightsControllers(BaseUsersCommon, HttpCase, PrescriptionCommon):

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_controller(self):
        private_rx = self.prescription_order
        portal_rx = self.prescription_order.copy()
        portal_rx.message_subscribe(self.user_portal.partner_id.ids)

        portal_rx._portal_ensure_token()
        token = portal_rx.access_token

        self.authenticate(None, None)

        # Test public user can't print an order without a token
        req = self.url_open(
            url='/my/orders/%s?report_type=pdf' % portal_rx.id,
            allow_redirects=False,
        )
        self.assertEqual(req.status_code, 303)

        # or with a random token
        req = self.url_open(
            url='/my/orders/%s?access_token=%s&report_type=pdf' % (
                portal_rx.id,
                "foo",
            ),
            allow_redirects=False,
        )
        self.assertEqual(req.status_code, 303)

        # but works fine with the right token
        req = self.url_open(
            url='/my/orders/%s?access_token=%s&report_type=pdf' % (
                portal_rx.id,
                token,
            ),
            allow_redirects=False,
        )
        self.assertEqual(req.status_code, 200)

        self.authenticate(self.user_portal.login, self.user_portal.login)

        # do not need the token when logged in
        req = self.url_open(
            url='/my/orders/%s?report_type=pdf' % portal_rx.id,
            allow_redirects=False,
        )
        self.assertEqual(req.status_code, 200)

        # but still can't access another order
        req = self.url_open(
            url='/my/orders/%s?report_type=pdf' % private_rx.id,
            allow_redirects=False,
        )
        self.assertEqual(req.status_code, 303)


@tagged('post_install', '-at_install')
class TestPrescriptionSignature(HttpCaseWithUserPortal):

    def test_01_portal_prescription_signature_tour(self):
        """The goal of this test is to make sure the portal user can sign RX."""

        portal_user_partner = self.partner_portal
        # create a RX to be signed
        prescription_order = self.env['prescription.order'].create({
            'name': 'test RX',
            'partner_id': portal_user_partner.id,
            'state': 'sent',
            'require_payment': False,
        })
        self.env['prescription.order.line'].create({
            'order_id': prescription_order.id,
            'product_id': self.env['product.product'].create({'name': 'A product'}).id,
        })

        # must be sent to the user so he can see it
        email_act = prescription_order.action_quotation_send()
        email_ctx = email_act.get('context', {})
        prescription_order.with_context(**email_ctx).message_post_with_source(
            self.env['mail.template'].browse(email_ctx.get('default_template_id')),
            subtype_xmlid='mail.mt_comment',
        )

        self.start_tour("/", 'prescription_signature', login="portal")
