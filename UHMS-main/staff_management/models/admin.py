from odoo import models, fields

class Admin(models.Model):
    _name = 'staff.admin'
    _description = 'Admin'

    staff_id = fields.Many2one('staff.management', string='Staff', required=True)
    role = fields.Char(string='Role')
