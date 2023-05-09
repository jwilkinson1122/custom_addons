# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PodiatryInactiveWizard(models.TransientModel):
    _name = 'podiatry.inactive.wizard'
    _description = 'Inactive Wizard'

    def _get_default_inactive_date(self):
        inactive_date = False
        if self.env.context.get('active_id'):
            inactive_date = self.env['podiatry.employee'].browse(self.env.context['active_id']).inactive_date
        return inactive_date or fields.Date.today()

    inactive_reason_id = fields.Many2one("podiatry.inactive.reason", default=lambda self: self.env['podiatry.inactive.reason'].search([], limit=1), required=True)
    inactive_description = fields.Html(string="Additional Information")
    inactive_date = fields.Date(string="Inactive Date", required=True, default=_get_default_inactive_date)
    employee_id = fields.Many2one(
        'podiatry.employee', string='Employee', required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )
    archive_private_address = fields.Boolean('Archive Private Address', default=True)

    def action_register_inactive(self):
        employee = self.employee_id
        if self.env.context.get('toggle_active', False) and employee.active:
            employee.with_context(no_wizard=True).toggle_active()
        employee.inactive_reason_id = self.inactive_reason_id
        employee.inactive_description = self.inactive_description
        employee.inactive_date = self.inactive_date

        if self.archive_private_address:
            # ignore contact links to internal users
            private_address = employee.address_home_id
            if private_address and private_address.active and not self.env['res.users'].search([('partner_id', '=', private_address.id)]):
                private_address.toggle_active()
