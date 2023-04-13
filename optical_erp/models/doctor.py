from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Doctor(models.Model):
    _name = "optical.dr"
    # _inherit = ['mail.thread',
    #             'mail.activity.mixin', 'image.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')
    practice_id = fields.Many2one(comodel_name='optical.practice', string='Practice')
    responsible_id = fields.Many2one(comodel_name='res.users', string="Created By", default=lambda self: self.env.user)
    is_doctor = fields.Boolean()
    doctor_id = fields.Many2many('res.partner', domain=[('is_doctor', '=', True)], string="Doctor", required=True)
    reference = fields.Char(string='Doctor Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    related_user_id = fields.Many2one(related='partner_id.user_id')
    address_id = fields.Many2one('res.partner', string="Doctor Address", )
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade', help='Partner-related data of the Doctor')
    other_partner_ids = fields.Many2many(comodel_name='res.partner', relation='optical_doctor_partners_rel', column1='doctor_id', column2='partner_id', string="Other Doctors")
    same_reference_doctor_id = fields.Many2one(comodel_name='optical.dr', string='Doctor with same Identity', compute='_compute_same_reference_doctor_id')
    role_ids = fields.Many2many(string='Role',comodel_name='optical.role')
    specialty_ids = fields.Many2many(string='Specialties', comodel_name='optical.specialty')
    
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_doctor_prescriptions(self):
        for records in self:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'domain': [('dr', '=', records.id)],
                'res_model': 'dr.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_dr': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['dr.prescription'].search_count([('dr', '=', records.id)])
            records.prescription_count = count
            
    @api.onchange('doctor_id')
    def _onchange_doctor(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.doctor_id
        self.address_id = address_id

    @api.depends('reference')
    def _compute_same_reference_doctor_id(self):
        for doctor in self:
            domain = [
                ('reference', '=', doctor.reference),
            ]

            origin_id = doctor._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            doctor.same_reference_doctor_id = bool(doctor.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)
    
    def _add_followers(self):
        for doctor in self:
            partner_ids = (doctor.user_id.partner_id |
                           doctor.responsible_id.partner_id).ids
            doctor.message_subscribe(partner_ids=partner_ids)

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)
    
    # @api.model
    # def create(self, vals):
    #     if not vals.get('notes'):
    #         vals['notes'] = 'New Doctor'
    #     if vals.get('reference', _('New')) == _('New'):
    #         vals['reference'] = self.env['ir.sequence'].next_by_code(
    #             'optical.dr.sequence') or _('New')
    #     practitioner = super(Doctor, self).create(vals)
    #     practitioner._add_followers()
    #     return practitioner

    def create_doctors(self, vals):
        print('.....res')
        self.is_doctor = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this doctor already created.'))
        else:
            self.create_users_button = False
        
        if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                'optical.dr.sequence') or _('New')  
            
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
    
    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Doctor, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate doctor.'))

    def unlink(self):
        self.partner_id.unlink()
        return super(Doctor, self).unlink()

