from odoo import fields, models


class Product(models.Model):
    _name = 'musicstore.product'
    _description = 'Product'

    # String
    cod = fields.Char('Cod', required=True, readonly=True, copy=False, default='New')
    name = fields.Char(
        'Title',
        required=True
    )

    # Numbers
    price = fields.Float('Song price', (5, 2), required=True)
    stock = fields.Integer()

    # Image
    image = fields.Binary('Cover')
