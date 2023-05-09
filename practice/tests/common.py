# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests import common


class TestPodiatryCommon(common.TransactionCase):

    def setUp(self):
        super(TestPodiatryCommon, self).setUp()

        self.res_users_podiatry_officer = mail_new_test_user(self.env, login='podiatryo', groups='base.group_user,podiatry.group_podiatry_user', name='POD Officer', email='podiatryo@example.com')
