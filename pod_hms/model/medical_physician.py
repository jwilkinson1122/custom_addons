# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_physician(models.Model):
    _name="medical.physician"
    _description = 'medical physician'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner','Physician',required=True)
    practice_partner_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)],string='Practice')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
    
    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice')
