from odoo import models, fields, api

# class PracticePartner(models.Model):
#     _name = 'res.partner'
#     _description = 'Practice Partner'

#     name = fields.Char(string='Partner Name', required=True)
#     description = fields.Char(string='Partner details')

class PracticePartner(models.Model):
        _inherit = "res.partner"
       
     
        is_patient = fields.Boolean(string='Patient')
        is_person = fields.Boolean(string="Person")
        is_doctor = fields.Boolean(string="Doctor")
        is_practice = fields.Boolean(string='Practice')
        # patient_ids = fields.One2many('medical.insurance','patient_id')

        # patient_ids = fields.One2many('pod_erp.practice','patient_id')
        # doctor_ids = fields.One2many('pod_erp.practice','doctor_id')
        reference = fields.Char('ID Number')