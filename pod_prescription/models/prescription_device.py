from odoo import models, fields, api


class PrescriptionDevice(models.Model):
    _name = 'prescription.device'
    _description = 'Prescription Orthotic Device'

    name = fields.Char(string='Device Name', required=True)
    description = fields.Text(string='Description')
    unit_price = fields.Float(string='Unit Price')
    quantity = fields.Integer(string='Quantity')    
    laterality = fields.Selection([
            ('lt_single', 'Left'),
            ('rt_single', 'Right'),
            ('bl_pair', 'Bilateral')
        ], string='Laterality', required=True, default='bl_pair')
    # left_only = fields.Boolean('Left Only')
    # right_only = fields.Boolean('Right Only')