from odoo import models, fields, api


class OrthoticSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Orthotic Sales Order'