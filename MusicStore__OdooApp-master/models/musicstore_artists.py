from odoo import fields, models, api


class Artists(models.Model):
    _name = 'musicstore.artists'
    _description = 'Artists'

    # String
    cod = fields.Char('Cod', required=True, readonly=True, copy=False, default='New')
    name = fields.Char('Name', required=True)
    surname = fields.Char('Surname')
    nickname = fields.Char()
    tlf = fields.Char('Phone')
    email = fields.Char('Email')

    @api.model
    def create(self, value):
        if value.get('cod', 'New') == 'New':
            value['cod'] = self.env['ir.sequence'].next_by_code('musicstore.artists') or 'New'
        result = super(Artists, self).create(value)
        return result
