# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prescriptions_spreadsheet_folder_id = fields.Many2one(
        'prescriptions.folder', related='company_id.prescriptions_spreadsheet_folder_id', readonly=False)
