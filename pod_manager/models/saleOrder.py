from odoo import models, fields, api


class DeviceSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Device Sales Order'
