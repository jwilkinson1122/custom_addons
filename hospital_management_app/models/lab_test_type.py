# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class LabTestType(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Lab Test Type Type'
    _name = 'lab.test.type'

    name = fields.Char(string='Name', required=True, tracking=True)
    fees = fields.Float(string='Fees', tracking=True)
    min_range = fields.Float(string='Minimum Range', tracking=True)
    max_range = fields.Float(string='Maximum Range', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='Unit')
    note = fields.Text(string='Note')
