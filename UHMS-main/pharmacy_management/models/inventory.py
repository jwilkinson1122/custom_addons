from odoo import models, fields, api

class Inventory(models.Model):
    _name = 'pharmacy.inventory'
    _description = 'Inventory'

    medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True)
    stock_in = fields.Integer(string='Stock In', required=True)
    stock_out = fields.Integer(string='Stock Out', required=True)
    current_stock = fields.Integer(string='Current Stock', compute='_compute_current_stock', store=True)

    @api.depends('stock_in', 'stock_out')
    def _compute_current_stock(self):
        for record in self:
            record.current_stock = record.stock_in - record.stock_out










# from odoo import models, fields

# class Inventory(models.Model):
#     _name = 'pharmacy.inventory'
#     _description = 'Inventory'

#     medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True)
#     stock_in = fields.Integer(string='Stock In', required=True)
#     stock_out = fields.Integer(string='Stock Out', required=True)
#     current_stock = fields.Integer(string='Current Stock', compute='_compute_current_stock', store=True)

#     def _compute_current_stock(self):
#         for record in self:
#             record.current_stock = record.medicine_id.quantity_available + record.stock_in - record.stock_out
#             record.medicine_id.quantity_available = record.current_stock
