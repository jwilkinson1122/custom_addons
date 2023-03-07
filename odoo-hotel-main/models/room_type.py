from odoo import api, fields, models


class RoomType(models.Model):
    _name = 'hotel.room_type'
    _description = 'List of Room Types'

    name = fields.Char(string='Name', required=True)
    price = fields.Integer(string='Price', required=True)
    description = fields.Char(string='Description')
