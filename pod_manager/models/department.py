from odoo import models, fields, api

# class PracticeDepartment(models.Model):
#     _name = 'pod.manager.department'
#     _description = 'Practice Department'

#     name = fields.Char(string='Department Name', required=True)
#     description = fields.Char(string='Department details')


class PracticeDepartment(models.Model):
    _inherit = "hr.department"
