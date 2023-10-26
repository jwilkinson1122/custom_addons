# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_prescription_minimum_threshold = fields.Float(string="Maximum Allowed Overdraft", readonly=False, related='company_id.prescription_minimum_threshold')
