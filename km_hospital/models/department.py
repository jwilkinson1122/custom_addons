from odoo import models, fields, api

# class HospitalDepartment(models.Model):
#     _name = 'kmhospital.department'
#     _description = 'Podiatry Department'

#     name = fields.Char(string='Department Name', required=True)
#     description = fields.Char(string='Department details')


class HospitalDepartment(models.Model):
    _inherit = "hr.department"
