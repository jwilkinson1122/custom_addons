# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class Partner(models.Model):
    _inherit = "res.partner"

    prescription_count = fields.Integer('Prescription Count', compute='_compute_prescription_count')

    def _compute_prescription_count(self):
        read_group_var = self.env['prescriptions.prescription']._read_group(
            [('partner_id', 'in', self.ids)],
            groupby=['partner_id'],
            aggregates=['__count'])

        prescription_count_dict = {partner.id: count for partner, count in read_group_var}
        for record in self:
            record.prescription_count = prescription_count_dict.get(record.id, 0)

    def action_see_prescriptions(self):
        self.ensure_one()
        return {
            'name': _('Prescriptions'),
            'domain': [('partner_id', '=', self.id)],
            'res_model': 'prescriptions.prescription',
            'type': 'ir.actions.act_window',
            'views': [(False, 'kanban')],
            'view_mode': 'kanban',
            'context': {
                "default_partner_id": self.id,
                "searchpanel_default_folder_id": False
            },
        }
