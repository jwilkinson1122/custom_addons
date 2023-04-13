# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.modules.module import get_module_resource

class Patient(models.Model):
    _name = "optical.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'patient_id'
    
    create_users_button = fields.Boolean()
    # user_id = fields.Many2one('res.users')
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')
    is_patient = fields.Boolean(string='Is Patient', tracking=True)
    patient_id = fields.Many2one('res.partner', domain=[('is_patient', '=', True)], string="Patient", required=True)
    dob = fields.Date()
    patient_age = fields.Integer(compute='_cal_age', readonly=True)
    doctor_id = fields.Many2one(comodel_name='optical.dr', required=True, string='Doctor')
    practice_id = fields.Many2one(comodel_name='optical.practice', required=True, string="Practice")
    reference = fields.Char(string='Patient Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    prescription_ids = fields.One2many(comodel_name='dr.prescription', inverse_name='patient_id', string="Prescriptions")
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade', help='Partner-related data of the Patient')

    notes = fields.Text(string="Notes")

    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")

    diagnosis = fields.Selection(selection=[
        ('plantar_fasciitis', 'Plantar Fasciitis'),
        ('diabetes', 'Diabetes'),
        ('other', 'Other'),
    ], string="Diagnosis")

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.patient_age = str(int(years))
            else:
                record.patient_age = 0
                
    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain.
        '''
        address_id = self.patient_id
        self.address_id = address_id

    address_id = fields.Many2one(
        'res.partner', string="Patient Address", )

    # @api.onchange('practice_id')
    # def onchange_practice_id(self):
    #     for rec in self:
    #         return {'domain': {'doctor_id': [('practice_id', '=', rec.practice_id.id)]}}
    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'doctor_id': [('practice_id', '=', rec.practice_id.id)]}}
        
    other_patient_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='optical_patient_partners_rel',
        column1='patient_id', column2='partner_id',
        string="Other Patients",
    )
        
    same_reference_patient_id = fields.Many2one(
        comodel_name='optical.patient',
        string='Patient with same Identity',
        compute='_compute_same_reference_patient_id',
    )

    @api.depends('reference')
    def _compute_same_reference_patient_id(self):
        for patient in self:
            domain = [
                ('reference', '=', patient.reference),
            ]

            origin_id = patient._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            patient.same_reference_patient_id = bool(patient.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)
                
                
    prescription_count = fields.Integer(string='Prescription Count', compute='_compute_prescription_count')

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['dr.prescription'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    def _valid_field_parameter(self, field, name):
            return name == 'sort' or super()._valid_field_parameter(field, name)
    
    @api.model
    def create(self,vals):
        prescription = self._context.get('prescription_id')
        res_partner_obj = self.env['res.partner']
        if prescription:
            val_1 = {'name': self.env['res.partner'].browse(vals['patient_id']).name}
            patient= res_partner_obj.create(val_1)
            vals.update({'patient_id': patient.id})
        if vals.get('date_of_birth'):
            dt = vals.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
            vals.update({'age':age} )
        if not vals.get('notes'):
                vals['notes'] = 'New Patient'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'optical.practice.sequence') or _('New')
        patient = super(Patient, self).create(vals)
        return patient
    # def create_patient(self):
    #     self.is_patient = True
    #     if len(self.partner_id.user_ids):
    #         raise UserError(_('User for this patient already created.'))
    #     else:
    #         self.create_users_button = False
    #     patient_id = []

    #     patient_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Patient')]).id)
    #     patient_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Internal User')]).id)
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Name ',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref("patient.view_create_user_wizard_form").id,
    #         'target': 'new',
    #         'res_model': 'res.users',
    #         'context': {'default_partner_id': self.partner_id.id, 'default_is_patient': True,
    #                     'default_groups_id': [(6, 0, patient_id)]}

    #     }
    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result
    
    user_id = fields.Many2one(
        comodel_name='res.users', string="User",
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users', string="Created By",
        default=lambda self: self.env.user,
    )
    
    def _add_followers(self):
        for patient in self:
            partner_ids = (patient.user_id.partner_id |
                           patient.responsible_id.partner_id).ids
            patient.message_subscribe(partner_ids=partner_ids)

    def write(self, values):
        result = super(Patient, self).write(values)
        if 'user_id' in values or 'other_patient_ids' in values:
            self._add_followers()
        return result

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'dr.prescription',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def unlink(self):
        self.partner_id.unlink()
        return super(Patient, self).unlink()