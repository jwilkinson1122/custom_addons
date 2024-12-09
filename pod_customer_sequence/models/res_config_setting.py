# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_create = fields.Boolean(
        "Auto Create Sequence - Individual / Company")
    auto_create_contact = fields.Boolean("Auto Create Sequence - Contacts")


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_create = fields.Boolean(
        string="Auto Create Sequence - Individual / Company",
        related='company_id.auto_create',
        readonly=False
    )
    auto_create_contact = fields.Boolean(
        string="Auto Create Sequence - Contacts",
        related='company_id.auto_create_contact',
        readonly=False
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        auto_create = self.env['ir.config_parameter'].sudo(
        ).get_param('auto_create')
        auto_create_contact = self.env['ir.config_parameter'].sudo(
        ).get_param('auto_create_contact')
        res.update(
            auto_create=auto_create,
            auto_create_contact=auto_create_contact,
        )
        return res

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('auto_create', self.auto_create)
        param.set_param('auto_create_contact', self.auto_create_contact)
        return res
