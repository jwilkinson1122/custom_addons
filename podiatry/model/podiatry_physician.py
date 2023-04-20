# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class podiatry_physician(models.Model):
    _name="podiatry.physician"
    _description = 'podiatry physician'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner','Physician',required=True)
    institution_partner_id = fields.Many2one('res.partner',domain=[('is_institution','=',True)],string='Institution')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
