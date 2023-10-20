# -*- coding: utf-8 -*-

from odoo import fields, models


class Channel(models.Model):
    _inherit = 'mail.channel'

    subscription_practice_ids = fields.Many2many(
        'pod.practice', string='POD Practices',
        help='Automatically subscribe members of those practices to the channel.')

    def _subscribe_users_automatically_get_members(self):
        """ Auto-subscribe members of a practice to a channel """
        new_members = super(Channel, self)._subscribe_users_automatically_get_members()
        for channel in self:
            new_members[channel.id] = list(
                set(new_members[channel.id]) |
                set((channel.subscription_practice_ids.member_ids.user_id.partner_id - channel.channel_partner_ids).ids)
            )
        return new_members

    def write(self, vals):
        res = super(Channel, self).write(vals)
        if vals.get('subscription_practice_ids'):
            self._subscribe_users_automatically()
        return res
