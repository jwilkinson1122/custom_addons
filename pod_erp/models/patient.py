from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Patient(models.Model):
    _name = "podiatry.patient"
    _inherits = {
        'res.partner': 'partner_id',
    }
    create_users_button = fields.Boolean()
    # partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
    #                              help='Partner-related data of the Patient')
    partner_id = fields.Many2one(comodel_name='res.partner', string="Patients", required=True, ondelete='restrict')
    is_patient = fields.Boolean()
    related_user_id = fields.Many2one(related='partner_id.user_id')
    prescription_count = fields.Integer(compute='get_prescription_count')
    dob = fields.Date()
    age = fields.Integer(compute='_cal_age',store=True,readonly=True)
    
    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.age = str(int(years))
            else:
                record.age = 0

    def open_patient_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription'),
                'view_type': 'form',
                'domain': [('patient', '=', records.id)],
                'res_model': 'podiatry.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_patient': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count([('patient', '=', records.id)])
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



