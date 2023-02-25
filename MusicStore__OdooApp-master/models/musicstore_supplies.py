from odoo import api, exceptions, fields, models


class Supplies(models.Model):
    _name = 'musicstore.supplies'
    _description = 'Supplies Request'
    _rec_name = 'user_id'

    # Numbers
    cod = fields.Char('Cod', required=True, readonly=True, copy=False, default='New')
    amount_disc = fields.Integer()
    amount_songs = fields.Integer()
    order_price = fields.Float(compute='_compute_orderprice', readonly=True)

    # Dates
    request_date = fields.Date(
        default=lambda s: fields.Date.today())

    # Others
    user_id = fields.Many2one(
        'res.users',
        'Salesperson',
        default=lambda s: s.env.uid)

    provider_id = fields.Many2one(
        'res.partner',
        'Provider',
        default=lambda s: s.env.uid)

    disc_id = fields.Many2one('musicstore.disc', string='Disc')
    songs_id = fields.Many2one('musicstore.song', string='Song')

    @api.model
    def create(self, value):
        if value.get('cod', 'New') == 'New':
            value['cod'] = self.env['ir.sequence'].next_by_code('musicstore.supplies') or 'New'
        result = super(Supplies, self).create(value)
        discos = result.disc_id
        for disco in discos:
            disco.stock += result.amount_disc

        canciones = result.songs_id
        for cancion in canciones:
            cancion.stock += result.amount_songs

        return result

    @api.onchange('user_id')
    def onchange_member_id(self):
        today = fields.Date.today()
        if self.request_date != today:
            self.request_date = fields.Date.today()
            return {
                'warning': {
                    'title': 'Changed Request Date',
                    'message': 'Request date changed to today.',
                }
            }

    @api.depends('disc_id', 'songs_id', 'amount_disc', 'amount_songs')
    def _compute_orderprice(self):
        totalDiscos = 0
        totalCancion = 0
        for disc in self.disc_id:
            totalDiscos += disc.price * self.amount_disc
        for song in self.songs_id:
            totalCancion += song.price * self.amount_songs
        self.order_price = totalDiscos + totalCancion
