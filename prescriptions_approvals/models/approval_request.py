

from odoo import fields, models, _


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _inherit = ['approval.request', 'prescriptions.mixin']

    prescriptions_count = fields.Integer(compute='_compute_prescriptions_count')
    prescriptions_enabled = fields.Boolean(related='company_id.prescriptions_approvals_settings')

    def _get_prescription_tags(self):
        return self.company_id.approvals_tag_ids

    def _get_prescription_folder(self):
        return self.company_id.approvals_folder_id

    def _get_prescription_partner(self):
        return self.partner_id

    def _check_create_prescriptions(self):
        return self.company_id.prescriptions_approvals_settings and super()._check_create_prescriptions()

    def _compute_prescriptions_count(self):
        grouped_data = self.env['prescriptions.prescription']._read_group(domain=[('res_model', '=', 'approval.request'),
                                                                          ('res_id', 'in', self.ids),
                                                                          ('active', '=', True)],
                                                                  groupby=['res_id'],
                                                                  aggregates=['__count'])
        mapped_data = dict(grouped_data)
        for record in self:
            record.prescriptions_count = mapped_data.get(record.id, 0)

    def action_get_attachment_view(self):
        if not self.company_id.prescriptions_approvals_settings:
            return super().action_get_attachment_view()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'prescriptions.prescription',
            'name': _('Prescriptions'),
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', 'approval.request'), ('res_id', 'in', self.ids)],
            'context': {
                'searchpanel_default_folder_id': self._get_prescription_folder().id,
                'default_res_model': 'approval.request',
                'default_res_id': self.ids[0],
            },
        }
