from odoo import fields, models, api


class Disc(models.Model):
    _inherit = 'musicstore.product'
    _name = 'musicstore.disc'
    _description = 'Disc'
    _order = 'name'

    # Date and Time
    date_published = fields.Date('Published on')
    duration = fields.Float(compute='_compute_sumaTotal')

    # Numbers
    price = fields.Float('Disc price', (5, 2), required=True)

    # Other
    disc_type = fields.Selection(
        [('cd', 'CD'),
         ('cassette', 'Cassette'),
         ('vinyl', 'Vinyl'),
         ('digital', 'Digital'),
         ('other', 'Other')],
        'Type'
    )

    company_id = fields.Many2one(
        'musicstore.recordcompany',
        string='Company Records'
    )

    group_ids = fields.Many2many(
        'musicstore.group',
        string='Groups'
    )

    song_ids = fields.Many2many(
        'musicstore.song',
        string='Songs'
    )

    @api.depends('song_ids')
    def _compute_sumaTotal(self):
        for disc in self:
            disc.duration = 0
            for song in disc.song_ids:
                disc.duration += song.time

    @api.model
    def create(self, value):
        if value.get('cod', 'New') == 'New':
            value['cod'] = self.env['ir.sequence'].next_by_code('musicstore.disc') or 'New'
        result = super(Disc, self).create(value)
        return result
