# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_physician(models.Model):
    _name = "podiatry.physician"
    _description = 'podiatry physician'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', 'Physician', required=True)
    institution_partner_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string='Institution')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
