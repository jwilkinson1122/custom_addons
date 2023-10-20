# -*- coding: utf-8 -*-

from odoo import fields, models


class PodDepartureWizard(models.TransientModel):
    _name = 'pod.deactivate.wizard'
    _description = 'Departure Wizard'

    def _get_default_deactivate_date(self):
        deactivate_date = False
        if self.env.context.get('active_id'):
            deactivate_date = self.env['pod.practitioner'].browse(self.env.context['active_id']).deactivate_date
        return deactivate_date or fields.Date.today()

    deactivate_reason_id = fields.Many2one("pod.deactivate.reason", default=lambda self: self.env['pod.deactivate.reason'].search([], limit=1), required=True)
    deactivate_description = fields.Html(string="Additional Information")
    deactivate_date = fields.Date(string="Departure Date", required=True, default=_get_default_deactivate_date)
    practitioner_id = fields.Many2one(
        'pod.practitioner', string='Practitioner', required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )
    archive_private_address = fields.Boolean('Archive Private Address', default=True)

    def action_register_deactivate(self):
        practitioner = self.practitioner_id
        if self.env.context.get('toggle_active', False) and practitioner.active:
            practitioner.with_context(no_wizard=True).toggle_active()
        practitioner.deactivate_reason_id = self.deactivate_reason_id
        practitioner.deactivate_description = self.deactivate_description
        practitioner.deactivate_date = self.deactivate_date

        if self.archive_private_address:
            # ignore contact links to internal users
            private_address = practitioner.private_address_id
            if private_address and private_address.active and not self.env['res.users'].search([('partner_id', '=', private_address.id)]):
                private_address.toggle_active()
