from odoo import models, fields, api


class Medicine(models.Model):
    _name = 'eclinic.medicine'
    _description = 'Information about medicines'

    name = fields.Char(string='Medicine Name', required=True)
    description = fields.Text(string='Description')
    dosage = fields.Float(string='Dosage')
    unit_price = fields.Float(string='Unit Price')
    quantity = fields.Integer(string='Quantity')    
    manufacturer = fields.Char(string='Manufacturer')
