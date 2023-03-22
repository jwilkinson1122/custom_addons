# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_practitioner(models.Model):
    _name="medical.practitioner"
    _description = 'medical practitioner'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner','Practitioner',required=True)
    practice_partner_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)],string='Practice')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
    
    practice_id = fields.Many2one(
        comodel_name='medical.practice',
        string='Practice')
    
    prescription_ids = fields.One2many(
        comodel_name='medical.prescription.order',
        inverse_name='practitioner_id',
        string='Prescriptions')
