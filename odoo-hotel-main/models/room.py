from odoo import api, fields, models


class Room(models.Model):
    _name = 'hotel.room'
    _description = 'List of Hotel Rooms'

    room_id = fields.Char(string='Room ID', required=True)
    name = fields.Char(string='Room Name', required=True)
    type = fields.Many2one(comodel_name='hotel.room_type',
                           string='Room Type', required=True)
    stock = fields.Integer(string='Stock', required=True)
    description = fields.Char(string='Description')
    price = fields.Integer(string='Price', readonly=True,
                           compute='_compute_price')

    image = fields.Binary(string='Image', attachment=True)

    @api.depends('type')
    def _compute_price(self):
        for record in self:
            record.price = record.type.price
