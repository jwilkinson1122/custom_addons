# -*- coding: utf-8 -*-

from odoo.addons.pod_manager.tests.common import TestPodCommon


class TestChannel(TestPodCommon):

    def setUp(self):
        super(TestChannel, self).setUp()

        self.channel = self.env['mail.channel'].create({'name': 'Test'})

        emp0 = self.env['pod.practitioner'].create({
            'user_id': self.res_users_pod_officer.id,
        })
        self.practice = self.env['pod.practice'].create({
            'name': 'Test Practice',
            'member_ids': [(4, emp0.id)],
        })

    def test_auto_subscribe_practice(self):
        self.assertEqual(self.channel.channel_partner_ids, self.env['res.partner'])

        self.channel.write({
            'subscription_practice_ids': [(4, self.practice.id)]
        })

        self.assertEqual(self.channel.channel_partner_ids, self.practice.mapped('member_ids.user_id.partner_id'))
