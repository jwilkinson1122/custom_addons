# -*- coding: utf-8 -*-


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    prescriptions_spreadsheet_folder_id = fields.Many2one('prescriptions.folder', check_company=True,
        default=lambda self: self.env.ref('prescriptions_spreadsheet.prescriptions_spreadsheet_folder', raise_if_not_found=False))
