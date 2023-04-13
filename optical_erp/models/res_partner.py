from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models,_

class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Is Patient', tracking=True)
    is_practice = fields.Boolean('Practice')
    is_practitioner = fields.Boolean('Practitioner')

    dob = fields.Date()
    age = fields.Integer(compute='_cal_age',store=True,readonly=True)
    prescription_count = fields.Integer(compute='get_prescription_count')
    
      # type = fields.Selection(selection_add=[("patient", "Patient Address"),("sale")])
    
    type = fields.Selection(selection_add=[('patient','Patient Address')])
    
    # type = fields.Selection(selection_add=[('early_payment', 'Early payment: Discount early payment')])

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name':_('Prescription History'),
                'view_type': 'form',
                'domain': [('customer', '=',records.id)],
                'res_model': 'dr.prescription',
                'view_id': False,
                'view_mode':'tree,form',
                'context':{'default_customer':self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['dr.prescription'].search_count([('customer','=',records.id)])
            records.prescription_count = count

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.age = str(int(years))
            else:
                record.age = 0














