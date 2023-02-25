from odoo import fields, models, api


class Song(models.Model):
    _inherit = 'musicstore.product'
    _name = 'musicstore.song'
    _description = 'Song'
    _order = 'name'

    # Date and Time
    time = fields.Float('Time', (3, 2))

    @api.model
    def create(self, value):
        if value.get('cod', 'New') == 'New':
            value['cod'] = self.env['ir.sequence'].next_by_code('musicstore.song') or 'New'
        result = super(Song, self).create(value)
        return result
