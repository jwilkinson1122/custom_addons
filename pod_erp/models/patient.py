from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Patient(models.Model):
    _name = "pod.patient"
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'partner_id'
    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Patient', required=True, help='Partner-related data of the Patient')
    patient_practice_id = fields.Many2one('res.partner',domain=[('is_company','=',True)],string='Practice')
    patient_practitioner_id = fields.Many2one('res.partner',domain=[('is_practitioner','=',True)],string='Practitioner')
    is_patient = fields.Boolean()
    dob = fields.Date()
    patient_age = fields.Integer(compute='_cal_age', store=True, readonly=True)

    related_user_id = fields.Many2one(related='partner_id.user_id')
    
    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.patient_age = str(int(years))
            else:
                record.patient_age = 0
    
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_patient_prescriptions(self):
        for records in self:
            return {
                'name': _('Patient Prescription'),
                'view_type': 'form',
                'domain': [('patient', '=', records.id)],
                'res_model': 'practitioner.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_patient': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['practitioner.prescription'].search_count([('patient', '=', records.id)])
            records.prescription_count = count

    def create_patients(self):
        print('.....res')
        self.is_patient = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this patient already created.'))
        else:
            self.create_users_button = False
        patient_id = []
        patient_id.append(self.env['res.groups'].search([('name', '=', 'Patients')]).id)
        patient_id.append(self.env['res.groups'].search([('name', '=', 'Internal User')]).id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("patient.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_patient': True,
                        'default_groups_id': [(6, 0, patient_id)]}
        }
        
    def unlink(self):
        self.partner_id.unlink()
        return super(Patient, self).unlink()



