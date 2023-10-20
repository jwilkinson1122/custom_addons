# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Partner(models.Model):
    _inherit = ['res.partner']

    practitioner_ids = fields.One2many(
        'pod.practitioner', 'private_address_id', string='Practitioners', groups="pod_manager.group_pod_user",
        help="Related practitioners based on their private address")
    practitioners_count = fields.Integer(compute='_compute_practitioners_count', groups="pod_manager.group_pod_user")

    def name_get(self):
        """ Override to allow an practitioner to see its private address in his profile.
            This avoids to relax access rules on `res.parter` and to add an `ir.rule`.
            (advantage in both security and performance).
            Use a try/except instead of systematically checking to minimize the impact on performance.
            """
        try:
            return super(Partner, self).name_get()
        except AccessError as e:
            if len(self) == 1 and self in self.env.user.practitioner_ids.mapped('private_address_id'):
                return super(Partner, self.sudo()).name_get()
            raise e

    def _compute_practitioners_count(self):
        for partner in self:
            partner.practitioners_count = len(partner.practitioner_ids)

    def action_open_practitioners(self):
        self.ensure_one()
        return {
            'name': _('Related Practitioners'),
            'type': 'ir.actions.act_window',
            'res_model': 'pod.practitioner',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.practitioner_ids.ids)],
        }
