# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class DiseaseStage(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Condition Stage'
    _name = 'condition.stage'

    name = fields.Char(string='Name', required=True, tracking=True)
    note = fields.Text(string='Note')
