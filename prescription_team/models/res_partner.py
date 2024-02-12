# -*- coding: utf-8 -*-


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    team_id = fields.Many2one(
        'crm.team', 'Prescription Team',
        help='If set, this Prescription Team will be used for prescription and assignments related to this partner')
