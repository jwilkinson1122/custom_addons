from odoo import models, fields, api

# class PodDepartment(models.Model):
#     _name = 'podmanager.department'
#     _description = 'Pod Department'

#     name = fields.Char(string='Department Name', required=True)
#     description = fields.Char(string='Department details')


class PodDepartment(models.Model):
    _inherit = "hr.department"
