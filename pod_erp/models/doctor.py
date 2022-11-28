from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Doctor(models.Model):
    _name = "pod.doctor"
    _inherits = {
        'res.partner': 'partner_id',
    }
    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')
    is_doctor = fields.Boolean()
    related_user_id = fields.Many2one(related='partner_id.user_id')
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_doctor_prescriptions(self):
        for records in self:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'domain': [('doctor', '=', records.id)],
                'res_model': 'doctor.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_doctor': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['doctor.prescription'].search_count([('doctor', '=', records.id)])
            records.prescription_count = count

    def create_doctors(self):
        print('.....res')
        self.is_doctor = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this patient already created.'))
        else:
            self.create_users_button = False
        doctor_id = []
        doctor_id.append(self.env['res.groups'].search([('name', '=', 'Doctors')]).id)
        doctor_id.append(self.env['res.groups'].search([('name', '=', 'Internal User')]).id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("doctor.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_doctor': True,
                        'default_groups_id': [(6, 0, doctor_id)]}
        }



