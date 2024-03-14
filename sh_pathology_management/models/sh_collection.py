# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api


class Collection(models.Model):
    _name = "sh.collection.center"
    _description = "Collection Description"
    _order = "id desc"

    name = fields.Char(translate=True, string="Name")
    image = fields.Binary(string="")
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict')
    zip = fields.Char(change_default=True)
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Phone")
    active = fields.Boolean(default=True)
    laboratory_id = fields.Many2one(
        'sh.lab.center', ondelete='cascade', index=True, copy=True, required="1")

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
