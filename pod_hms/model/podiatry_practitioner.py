# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_practitioner(models.Model):
    _name = "podiatry.practitioner"
    _description = 'podiatry practitioner'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', 'Practitioner', required=True)
    practice_partner_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string='Medical Practice')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
