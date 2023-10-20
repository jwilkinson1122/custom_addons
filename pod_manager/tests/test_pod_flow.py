# -*- coding: utf-8 -*-

from odoo.addons.pod_manager.tests.common import TestPodCommon


class TestPodFlow(TestPodCommon):

    def setUp(self):
        super(TestPodFlow, self).setUp()
        self.practice_role = self.env['pod.practice'].create({
            'name': 'IT Manager',
        })
        self.role_technical = self.env['pod.role'].create({
            'name': 'Systems Admin',
            'practice_id': self.practice_role.id,
        })
        self.practitioner_niv = self.env['pod.practitioner'].create({
            'name': 'Michael Rhodes',
        })
        self.role_technical = self.role_technical.with_user(self.res_users_pod_officer.id)
        self.practitioner_niv = self.practitioner_niv.with_user(self.res_users_pod_officer.id)

  