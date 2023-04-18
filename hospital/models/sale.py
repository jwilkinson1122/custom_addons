from odoo import fields, models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    sale_details = fields.Char(
        string='sale_details',
        required=False)
