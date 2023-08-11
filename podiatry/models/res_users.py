# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    company_sign = fields.Text('Signature')
    
    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if "company_ids" in vals:
            res.partner_id.company_ids = vals["company_ids"]
        if "company_id" in vals and res.partner_id.company_ids:
            res.partner_id.company_id = vals["company_id"]
        return res

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if "company_ids" in vals:
            for user in self.sudo():
                if user.partner_id.company_ids:
                    user.partner_id.company_ids = vals["company_ids"]
        if "company_id" in vals:
            for user in self.sudo():
                if user.partner_id.company_ids:
                    user.partner_id.company_ids = [(4, vals["company_id"])]
        return res

class UserApiKey(models.Model):
    _inherit = 'res.users.apikeys'

    company_sign = fields.Text('Signature ')