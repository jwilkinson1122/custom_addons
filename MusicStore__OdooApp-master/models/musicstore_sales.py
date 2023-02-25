from odoo import api, exceptions, fields, models


class Sales(models.Model):
    _name = 'musicstore.sales'
    _description = 'Sales Request'
    _rec_name = 'user_id'

    cod = fields.Char('Cod', required=True, readonly=True, copy=False, default='New')
    user_id = fields.Many2one(
        'res.users',
        'Salesperson',
        default=lambda s: s.env.uid)
    sales_date = fields.Date(
        default=lambda s: fields.Date.today())

    disc_ids = fields.Many2many('musicstore.disc', string='Discs')
    song_ids = fields.Many2many('musicstore.song', string='Songs')
    order_price = fields.Float(compute='_compute_orderprice', readonly=True)

    @api.model
    def create(self, value):
        if value.get('cod', 'New') == 'New':
            value['cod'] = self.env['ir.sequence'].next_by_code('musicstore.sales') or 'New'
        result = super(Sales, self).create(value)
        discos = result.disc_ids
        for disco in discos:
            if disco.stock == 0:
                raise exceptions.ValidationError(
                    'No copies available for book %s' % disco.stock
                )
            else:
                disco.stock = disco.stock - 1
        canciones = result.song_ids
        for cancion in canciones:
            if cancion.stock == 0:
                raise exceptions.ValidationError(
                    'No copies available for book %s' % cancion.stock
                )
            else:
                cancion.stock = cancion.stock - 1
        return result

    @api.onchange('user_id')
    def onchange_member_id(self):
        today = fields.Date.today()
        if self.sales_date != today:
            self.sales_date = fields.Date.today()
            return {
                'warning': {
                    'title': 'Changed Request Date',
                    'message': 'Request date changed to today.',
                }
            }

    @api.depends('disc_ids', 'song_ids')
    def _compute_orderprice(self):
        totalDiscos = 0
        totalCancion = 0
        for disc in self.disc_ids:
            totalDiscos += disc.price
        for song in self.song_ids:
            totalCancion += song.price
        self.order_price = totalDiscos + totalCancion


