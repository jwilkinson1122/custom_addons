from odoo import models, fields, api


class Insurance(models.Model):
    _name = 'eclinic.insurance'
    _description = 'Insurance'

    name = fields.Char(string='Name', required=True)
    address = fields.Text(string='Address')    
    contact = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')
    policies = fields.One2many('eclinic.insurance.policy', 'insurance_id', string='Policies')
