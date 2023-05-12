from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Practitioner(models.Model):
    _name = "pod.practitioner"
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'partner_id'
    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Practitioner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Practitioner')
    practice_partner_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)],string='Practice')
    is_practitioner = fields.Boolean()
    related_user_id = fields.Many2one(related='partner_id.user_id')
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_practitioner_prescriptions(self):
        for records in self:
            return {
                'name': _('Practitioner Prescription'),
                'view_type': 'form',
                'domain': [('practitioner', '=', records.id)],
                'res_model': 'practitioner.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_practitioner': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['practitioner.prescription'].search_count([('practitioner', '=', records.id)])
            records.prescription_count = count

    def create_practitioners(self):
        print('.....res')
        self.is_practitioner = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this practitioner already created.'))
        else:
            self.create_users_button = False
        practitioner_id = []
        practitioner_id.append(self.env['res.groups'].search([('name', '=', 'Practitioners')]).id)
        practitioner_id.append(self.env['res.groups'].search([('name', '=', 'Internal User')]).id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("practitioner.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_practitioner': True,
                        'default_groups_id': [(6, 0, practitioner_id)]}
        }
        
    def unlink(self):
        self.partner_id.unlink()
        return super(Practitioner, self).unlink()



