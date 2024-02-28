# -*- coding: utf-8 -*-


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    prescriptions_device_settings = fields.Boolean(default=True)
    prescriptions_device_folder = fields.Many2one(
        'prescriptions.folder',
        string="Device Workspace",
        default=lambda self: self.env.ref('prescriptions_device.prescriptions_device_folder', raise_if_not_found=False),
        domain="['|', ('company_id', '=', False), ('company_id', '=', id)]",
    )
    prescriptions_device_tags = fields.Many2many('prescriptions.tag', 'prescriptions_device_tags_table')
