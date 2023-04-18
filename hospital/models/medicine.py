from odoo import fields, models, api


class Medicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'Description'
    _rec_name = 'name'
    name = fields.Char()

    description = fields.Text(
        string="Description",
        required=False)

    usage_type = fields.Selection(
        string='Usage_type',
        selection=[('Tablet', 'Tablet'),
                   ('patches', 'patches'),
                   ('Liquid', 'Liquid'),
                   ('Capsules', 'Capsules'),
                   ('Injections', 'Injections'),
                   ],
        required=False, )

    barcode = fields.Char(
        string='Barcode',
        required=False)

    sale_price = fields.Float(
        string='Sale_price',
        required=False)

    scientific_name = fields.Char(
        string='Scientific_name',
        required=False)

    originator = fields.Char(
        string='Originator',
        required=False,

    )

    taxes = fields.Float(
        string='Taxes %',
        required=False,

    )

    order_serial = fields.One2many(
        comodel_name='hospital.sale.medicine',
        inverse_name='medicine_name',
        string='Order serial',
        required=False)

    sale_price_after_taxes = fields.Float(
        string='sale_price_after_taxes',
        required=False,
        compute='price_after_taxes'
    )

    stock_start = fields.Integer(
        string='Stock_start',
        required=False,
        default=100
    )

    quantity_available = fields.Float(compute='get_quantity', store=True)
    quantity_sold = fields.Float(compute='get_sold_quantity', store=True)

    @api.depends('order_serial')
    def get_sold_quantity(self):
        for rec in self:
            rec.quantity_sold = sum(rec.order_serial.mapped('quantity'))

    @api.depends('order_serial')
    def get_quantity(self):
        for record in self:
            record.quantity_available = record.stock_start - sum(record.order_serial.mapped('quantity'))

    def price_after_taxes(self):
        # print(self)
        # print(self.sale_price)
        # print(self.taxes)
        for record in self:
            record.sale_price_after_taxes = record.sale_price + (record.sale_price * record.taxes)
            # record.sale_price_after_taxes=30
            # print(record)
