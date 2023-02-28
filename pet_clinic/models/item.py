from odoo import models, fields, api, _


class Item(models.Model):
    _name = 'pet_clinic.item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _sql_constraints = [
        ('internal_reference_unique', 'unique(internal_reference)',
         'internal reference already exists!')
    ]

    name = fields.Char(string='Name', required=True)
    internal_reference = fields.Char(string='Internal Reference', default='')
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    price = fields.Float(string='Price')
    item_type = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service')
    ], default='service', string='Type', required=True)
    image = fields.Binary(string='Image')
    amount = fields.Integer(string='Amount')
    description = fields.Text(string='Description')

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    item_category = fields.Many2one(
        'pet_clinic.item.category', string='Category')

    # Doctor
    doctor = fields.Many2one('pet_clinic.doctor')

    @api.depends('name', 'internal_reference')
    def _compute_fields_rec_name(self):
        for item in self:
            item.rec_name = '{} [{}]'.format(item.name, item.name)


class ItemCategory(models.Model):
    _name = 'pet_clinic.item.category'

    name = fields.Char(string='Name', required=True)
