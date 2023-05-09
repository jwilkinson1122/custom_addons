# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Partner(models.Model):
    _inherit = ['res.partner']

    employee_ids = fields.One2many(
        'podiatry.employee', 'address_home_id', string='Employees', groups="podiatry.group_podiatry_user",
        help="Related employees based on their private address")
    employees_count = fields.Integer(compute='_compute_employees_count', groups="podiatry.group_podiatry_user")

    def name_get(self):
        """ Override to allow an employee to see its private address in his profile.
            This avoids to relax access rules on `res.parter` and to add an `ir.rule`.
            (advantage in both security and performance).
            Use a try/except instead of systematically checking to minimize the impact on performance.
            """
        try:
            return super(Partner, self).name_get()
        except AccessError as e:
            if len(self) == 1 and self in self.env.user.employee_ids.mapped('address_home_id'):
                return super(Partner, self.sudo()).name_get()
            raise e

    def _compute_employees_count(self):
        for partner in self:
            partner.employees_count = len(partner.employee_ids)

    def action_open_employees(self):
        self.ensure_one()
        return {
            'name': _('Related Employees'),
            'type': 'ir.actions.act_window',
            'res_model': 'podiatry.employee',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.employee_ids.ids)],
        }
