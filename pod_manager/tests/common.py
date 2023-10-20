# -*- coding: utf-8 -*-

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests import common


class TestPodCommon(common.TransactionCase):

    def setUp(self):
        super(TestPodCommon, self).setUp()

        self.res_users_pod_officer = mail_new_test_user(self.env, login='hro', groups='base.group_user,pod_manager.group_pod_user', name='POD Officer', email='hro@example.com')
