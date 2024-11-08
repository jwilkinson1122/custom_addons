from odoo import models, fields

class Technician(models.Model):
    _name = 'staff.technician'
    _description = 'Technician'

    staff_id = fields.Many2one('staff.management', string='Staff', required=True)
    expertise = fields.Char(string='Expertise Area')
