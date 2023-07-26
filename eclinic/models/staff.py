from odoo import models, fields, api


class Staff(models.Model):
    _name = 'eclinic.staff'
    _description = 'Information about staff'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Char(string='Address')
    role = fields.Selection([('receptionist', 'Receptionist'), ('nurse', 'Nurse'), ('administrator', 'Administrator')], string='Role')
    is_active = fields.Boolean(string='Active', default=True)

    def toggle_active(self):
        for record in self:
            record.is_active = True

    def toggle_inactive(self):
        for record in self:
            record.is_active = False