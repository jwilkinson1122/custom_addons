# -*- coding: utf-8 -*-


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    prescriptions_account_settings = fields.Boolean()
    account_folder = fields.Many2one('prescriptions.folder', string="Accounting Workspace", check_company=True,
                                     default=lambda self: self.env.ref('prescriptions.prescriptions_finance_folder',
                                                                       raise_if_not_found=False)
                                     )
