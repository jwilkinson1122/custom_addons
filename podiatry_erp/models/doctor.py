from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Doctor(models.Model):
    _name = "podiatry.doctor"
    _inherits = {'res.partner': 'partner_id', }
    _description = 'doctor'
    # _rec_name = 'partner_id'

    @api.onchange('partner_id')
    def _onchange_doctor(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.partner_id
        self.partner_address_id = address_id

    create_users_button = fields.Boolean()
    # partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
    #                              help='Partner-related data of the Doctor')
    partner_id = fields.Many2one('res.partner', 'Doctor')
    practice_partner_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string='Medical Practice')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
    partner_address_id = fields.Many2one('res.partner', string="Address", )

    is_doctor = fields.Boolean()

    related_user_id = fields.Many2one(related='partner_id.user_id')

    prescription_ids = fields.One2many(
        'podiatry.prescription', 'doctor', string='Prescriptions')

    prescription_count = fields.Integer(compute='get_prescription_count')

    # doctor_id = fields.Many2one('res.partner', domain=[(
    #     'is_doctor', '=', True)], string="doctor", required=True)
    name = fields.Char(string='ID', readonly=True)

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    #  def print_report(self):
    #         return self.env.ref('basic_hms.report_print_doctor_card').report_action(self)

    def open_podiatry_prescriptions(self):
        for records in self:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'domain': [('doctor', '=', records.id)],
                'res_model': 'podiatry.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_doctor': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count(
                [('doctor', '=', records.id)])
            records.prescription_count = count

    # def create_doctors(self):
    #     print('.....res')
    #     self.is_doctor = True
    #     if len(self.partner_id.user_ids):
    #         raise UserError(_('User for this patient already created.'))
    #     else:
    #         self.create_users_button = False
    #     doctor_id = []
    #     doctor_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Doctors')]).id)
    #     doctor_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Internal User')]).id)

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Name ',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref("doctor.view_create_user_wizard_form").id,
    #         'target': 'new',
    #         'res_model': 'res.users',
    #         'context': {'default_partner_id': self.partner_id.id, 'default_is_doctor': True,
    #                     'default_groups_id': [(6, 0, doctor_id)]}
    #     }

    @api.model
    def create(self, val):
        prescription = self._context.get('prescription_id')
        res_partner_obj = self.env['res.partner']
        if prescription:
            val_1 = {'name': self.env['res.partner'].browse(
                val['doctor_id']).name}
            doctor = res_partner_obj.create(val_1)
            val.update({'doctor_id': doctor.id})

        doctor_id = self.env['ir.sequence'].next_by_code('podiatry.doctor')
        if doctor_id:
            val.update({
                'name': doctor_id,
            })
        # result = super(Doctor, self).create(val)
        # return result
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

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
