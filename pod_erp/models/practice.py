# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class Practice(models.Model):
    _name = 'pod.practice'
    _description = 'Medical Practice'
    _rec_name = 'practice_id'

    number = fields.Char('Number')
    # medical_insurance_partner_id = fields.Many2one('res.partner','Owner',required=True)
    partner_id = fields.Many2one("res.partner", string="Practice", index=True, tracking=True)
    # patient_id = fields.Many2one('res.partner', 'Owner')
    practice_type = fields.Selection([('clinic', 'Clinic'),
                                      ('hospital', 'Hospital'),
                                      ('multi', 'Multi-Hospital'),
                                      ('military', 'Military Medical Center'),
                                      ('other', 'Other')],
                                     string="Practice Type")
    practice_id = fields.Many2one('res.partner',domain=[('is_practice','=',True)],string='Practice')
 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
