from odoo import api, fields, models


class Additional(models.Model):
    _name = 'hotel.additional'
    _description = 'List of Additional Packs'

    name = fields.Char(string='Name', required=True)
    price = fields.Integer(string='Price')
    description = fields.Char(string='Description')
