# -*- coding: utf-8 -*-


from odoo import models, fields


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    tag_ids = fields.Many2many('prescriptions.tag')
    folder_id = fields.Many2one('prescriptions.folder',
                                help="By defining a folder, the upload activities will generate a prescription")
