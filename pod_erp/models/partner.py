from odoo import models, fields, api

# class PracticePartner(models.Model):
#     _name = 'pod_erp.partner'
#     _description = 'Practice Partner'

#     name = fields.Char(string='Partner Name', required=True)
#     description = fields.Char(string='Partner details')

class PracticePartner(models.Model):
        _inherit = "res.partner"