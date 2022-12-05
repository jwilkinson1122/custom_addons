from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    is_location = fields.Boolean('Practice')
    is_doctor = fields.Boolean('Doctor')
    is_patient = fields.Boolean('Patient')
    reference = fields.Char('ID Number')

    dob = fields.Date()
    age = fields.Integer(compute='_cal_age', store=True, readonly=True)
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription'),
                'view_type': 'form',
                'domain': [('customer', '=', records.id)],
                'res_model': 'medical.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_customer': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['medical.prescription'].search_count(
                [('customer', '=', records.id)])
            records.prescription_count = count

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.age = str(int(years))
            else:
                record.age = 0
