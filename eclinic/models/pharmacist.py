from odoo import models, fields, api


class Pharmacist(models.Model):
    _name = 'eclinic.pharmacist'
    _description = 'Pharmacist'

    clinic_id = fields.Many2many('clinic', string='Clinic')
    name = fields.Char(string='Pharmacist Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    address = fields.Text(string='Address')
    contact_number = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')