from odoo import models, fields, api, _


class ShellType(models.Model):
    _name = "shell.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _sql_constraints = [
        ('internal_reference_unique', 'unique(internal_reference)',
         'internal reference already exists!')
    ]

    name = fields.Char(required=True)
    internal_reference = fields.Char(string='Internal Reference', default='')
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    price = fields.Float(string='Price')
    item_type = fields.Selection([
        ('product', 'Product'),
        ('accommodation', 'Accommodation'),
        ('service', 'Service')
    ], default='product', string='Type', required=True)
    image = fields.Binary("Image", max_width=1920,
                          max_height=1920, widget=True)
    amount = fields.Integer(string='Amount')
    description = fields.Text(string='Description')

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    # item_category = fields.Many2one(
    #     'product.category', related='product_id.categ_id')

    item_category = fields.Many2one(
        'product.category', string="Product Category")

    product_uom_id = fields.Many2one(
        'uom.uom', string='Product UOM', required=True)

    # Practice
    practice = fields.Many2one('custom_orthotics.practice')

    @api.depends('name', 'internal_reference')
    def _compute_fields_rec_name(self):
        for item in self:
            item.rec_name = '{} [{}]'.format(item.name, item.name)


class ShellTypes(models.Model):
    _name = "shell.collection"
    description = fields.Text(string='Description')
    name = fields.Char(required=True)
    # type = fields.Many2one('shell.type', string='Type')
    type = fields.Many2many(comodel_name='shell.type', string='Type')
    image = fields.Binary("Image", max_width=1920,
                          max_height=1920, widget=True)


class ShellLength(models.Model):
    _name = "shell.length"

    name = fields.Char(required=True)
    description = fields.Text(string='Description')
