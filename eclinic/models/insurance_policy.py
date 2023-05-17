from odoo import models, fields, api


class Policy(models.Model):
    _name = 'eclinic.insurance.policy'
    _description = 'Information about insurance policies'

    insurance_id = fields.Many2one('eclinic.insurance', string='Insurance', required=True)
    number = fields.Char(string='Policy Number', required=True)
    description = fields.Char(string='Name', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    holder = fields.Char(string='Policy Holder')
    coverage_amount = fields.Float(string='Coverage Amount')
