# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prescriptions_device_settings = fields.Boolean(
        related='company_id.prescriptions_device_settings', readonly=False, string="Device")
    prescriptions_device_folder = fields.Many2one(
        'prescriptions.folder', related='company_id.prescriptions_device_folder', readonly=False, string="Device Workspace")
    prescriptions_device_tags = fields.Many2many(
        'prescriptions.tag', related='company_id.prescriptions_device_tags', readonly=False, string="Device Default Tags")
