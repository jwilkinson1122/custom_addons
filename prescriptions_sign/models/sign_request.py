# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class SignRequest(models.Model):
    _name = 'sign.request'
    _inherit = ['sign.request', 'prescriptions.mixin']

    def _get_prescription_tags(self):
        return self.template_id.prescriptions_tag_ids

    def _get_prescription_folder(self):
        return self.template_id.folder_id
