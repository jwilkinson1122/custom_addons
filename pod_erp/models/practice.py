from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Practice(models.Model):
    _name = "podiatry.practice"
    _inherits = {
        'res.partner': 'partner_id',
    }
    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Practice')
    is_practice = fields.Boolean()
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_practice_prescriptions(self):
        for records in self:
            return {
                'name': _('Practice Prescription'),
                'view_type': 'form',
                'res_model': 'practitioner.prescription',
                'domain': [('practice', '=', records.id)],
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_practice': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['practitioner.prescription'].search_count([('practice', '=', records.id)])
            records.prescription_count = count

    def create_practices(self):
        print('.....res')
        self.is_practice = True
        if len(self.partner_id):
            raise UserError(_('Partner already created.'))
        practice_id = []
        practice_id.append(self.env['res.groups'].search([('name', '=', 'Practices')]).id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("practice.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_practice': True,
                        'default_groups_id': [(6, 0, practice_id)]}
        }



