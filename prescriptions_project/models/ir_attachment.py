# -*- coding: utf-8 -*-



from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = ['ir.attachment']

    prescription_ids = fields.One2many('prescriptions.prescription', 'attachment_id')
