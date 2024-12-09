# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_ref = fields.Char(string='Customer Number', related='ref')

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if(
            self.env['ir.config_parameter'].sudo().get_param('auto_create') and
            not self.env['ir.config_parameter'].sudo().get_param('auto_create_contact') and
            not res.parent_id and
            not res.ref
        ):
            seq = self.env['ir.sequence'].next_by_code('res.partner')
            res.ref = seq
        elif(
            self.env['ir.config_parameter'].sudo().get_param('auto_create') and
            self.env['ir.config_parameter'].sudo().get_param('auto_create_contact') and
            not res.ref
        ):
            seq = self.env['ir.sequence'].next_by_code('res.partner')
            res.ref = seq
        return res

    def action_create_sequence(self):
        if not self.ref:
            seq = self.env['ir.sequence'].next_by_code('res.partner')
            self.ref = seq
