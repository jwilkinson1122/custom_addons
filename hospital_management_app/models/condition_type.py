# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ConditionType(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Condition Type'
    _name = 'condition.type'

    name = fields.Char(string='Name', required=True, tracking=True)
    fees = fields.Float(string='Fees')
    note = fields.Text(string='Note')
