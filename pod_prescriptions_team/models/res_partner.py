# -*- coding: utf-8 -*-


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    team_id = fields.Many2one(
        'crm.team', 'Prescriptions Team',
        help='If set, this Prescriptions Team will be used for prescriptions and assignments related to this partner')
