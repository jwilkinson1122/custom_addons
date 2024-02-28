# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class SignTemplate(models.Model):
    _name = 'sign.template'
    _inherit = ['sign.template', 'prescriptions.mixin']

    folder_id = fields.Many2one('prescriptions.folder', 'Signed Prescription Workspace')
    prescriptions_tag_ids = fields.Many2many('prescriptions.tag', string="Signed Prescription Tags")

    @api.model_create_multi
    def create(self, vals_list):
        # In the super(), if an attachment is already attached to a record, a copy of the original attachment will be
        # created and used for the template. Here if the attachment is only used for Prescription, we directly reuse it for
        # the template by unlinking the relationships and call super() with_context no_prescription.
        self.env['ir.attachment'].browse([vals.get('attachment_id') for vals in vals_list])\
            .filtered(lambda att: att.res_model == 'prescriptions.prescription')\
            .write({'res_model': False, 'res_id': 0})
        return super(SignTemplate, self.with_context(no_prescription=True))\
            .create(vals_list)\
            .with_context(no_prescription=bool(self._context.get('no_prescription')))

    def _get_prescription_tags(self):
        return self.prescriptions_tag_ids

    def _get_prescription_folder(self):
        return self.folder_id
