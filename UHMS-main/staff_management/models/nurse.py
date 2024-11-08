from odoo import models, fields

class Nurse(models.Model):
    _name = 'staff.nurse'
    _description = 'Nurse'

    staff_id = fields.Many2one('staff.management', string='Staff', required=True)
    department = fields.Char(string='Department')
