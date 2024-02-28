# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionsFolderSetting(models.Model):
    _name = 'prescriptions.account.folder.setting'
    _description = 'Journal and Folder settings'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company,
                                 ondelete='cascade')
    journal_id = fields.Many2one('account.journal', required=True)
    folder_id = fields.Many2one('prescriptions.folder', string="Workspace", required=True)
    tag_ids = fields.Many2many('prescriptions.tag', string="Tags")

    _sql_constraints = [
        ('journal_unique', 'unique (journal_id)', "A setting already exists for this journal"),
    ]
