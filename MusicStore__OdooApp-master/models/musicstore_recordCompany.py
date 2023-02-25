from odoo import fields, models, api


class recordCompany(models.Model):
    _name = 'musicstore.recordcompany'
    _description = 'Record Company'
    cod = fields.Char('Cod', required=True, readonly=True, copy=False, default='New')
    name = fields.Char(
        'Name',
        required=True
    )
    address = fields.Char()
    tlf = fields.Char('Phone')

    discs_id = fields.One2many(
        'musicstore.disc',
        'company_id',
        string='Discs'
    )

    @api.model
    def create(self, value):
        if value.get('cod', 'New') == 'New':
            value['cod'] = self.env['ir.sequence'].next_by_code('musicstore.recordcompany') or 'New'
        result = super(recordCompany, self).create(value)
        return result
