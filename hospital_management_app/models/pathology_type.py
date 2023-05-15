# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class PathologyType(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Pathology Type'
    _name = 'pathology.type'

    name = fields.Char(string='Name', required=True, tracking=True)
    fees = fields.Float(string='Fees', tracking=True)
    note = fields.Text(string='Note')
