from odoo import models, fields, api

class Prescription(models.Model):
    _name = 'pharmacy.prescription'
    _description = 'Prescription'

    #patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    #doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    medicine_ids = fields.Many2many('pharmacy.medicine', string='Medicines', required=True)
    date_prescribed = fields.Date(string='Date Prescribed', default=fields.Date.today)
    dosage = fields.Char(string='Dosage')
    frequency = fields.Char(string='Frequency')






# from odoo import models, fields, api

# class Prescription(models.Model):
#     _name = 'pharmacy.prescription'
#     _description = 'Prescription'

#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
#     medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True)
#     dosage = fields.Char(string='Dosage')
#     frequency = fields.Char(string='Frequency')
#     duration = fields.Integer(string='Duration (days)', required=True)
#     notes = fields.Text(string='Additional Notes')

#     date_prescribed = fields.Date(string='Date Prescribed', default=fields.Date.context_today)
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('confirmed', 'Confirmed'),
#         ('completed', 'Completed'),
#     ], string='Status', default='draft')

#     @api.onchange('medicine_id')
#     def _onchange_medicine(self):
#         if self.medicine_id:
#             self.dosage = self.medicine_id.description

#     def action_confirm(self):
#         self.state = 'confirmed'

#     def action_complete(self):
#         self.state = 'completed'
