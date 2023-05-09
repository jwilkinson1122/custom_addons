# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.podiatry.tests.common import TestPodiatryCommon


class TestChannel(TestPodiatryCommon):

    def setUp(self):
        super(TestChannel, self).setUp()

        self.channel = self.env['mail.channel'].create({'name': 'Test'})

        emp0 = self.env['podiatry.employee'].create({
            'user_id': self.res_users_podiatry_officer.id,
        })
        self.practice = self.env['podiatry.practice'].create({
            'name': 'Test Practice',
            'member_ids': [(4, emp0.id)],
        })

    def test_auto_subscribe_practice(self):
        self.assertEqual(self.channel.channel_partner_ids, self.env['res.partner'])

        self.channel.write({
            'subscription_practice_ids': [(4, self.practice.id)]
        })

        self.assertEqual(self.channel.channel_partner_ids, self.practice.mapped('member_ids.user_id.partner_id'))
