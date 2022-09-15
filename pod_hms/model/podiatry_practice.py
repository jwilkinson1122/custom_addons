from odoo import api, fields, models, _
from odoo.exceptions import UserError


class podiatry_practice(models.Model):
    _name = "podiatry.practice"
    _inherits = {
        'res.partner': 'partner_id',
    }
    # create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Related Practice', required=True, ondelete='restrict',
                                 help='Partner-related data of the Practice')
    is_practice = fields.Boolean()
    # related_user_id = fields.Many2one(related='partner_id.user_id')

    # practice_partner_id = fields.Many2one(
    #     'res.partner', domain=[('is_practice', '=', True)], string='Medical Practice')
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_practice_prescriptions(self):
        for records in self:
            return {
                'name': _('Practice Prescription'),
                'view_type': 'form',
                'domain': [('doctor_id', '=', records.id)],
                'res_model': 'podiatry.prescription.order',
                'view_id': False,
                'view_mode': 'tree,form',
                # 'context': {'default_dr': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription.order'].search_count(
                [('doctor_id', '=', records.id)])
            records.prescription_count = count

    # def create_users(self):
    #     print('.....res')
    #     self.is_practitioner = True
    #     if len(self.partner_id.user_ids):
    #         raise UserError(_('User for this patient already created.'))
    #     else:
    #         self.create_users_button = False
    #     practice_id = []
    #     practice_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Doctors')]).id)
    #     practice_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Internal User')]).id)

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Name ',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref("pod_erp.view_create_user_wizard_form").id,
    #         'target': 'new',
    #         'res_model': 'res.users',
    #         'context': {'default_partner_id': self.partner_id.id, 'default_is_practitioner': True,
    #                     'default_groups_id': [(6, 0, practice_id)]}
    #     }
