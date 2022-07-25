# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class pod_doctor(models.Model):
    _name = "pod.doctor"
    _description = 'pod doctor'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', 'Doctor', required=True)
    practice_partner_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string=' Practice')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
