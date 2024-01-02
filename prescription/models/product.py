# -*- coding: utf-8 -*-


from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    def _count_returned_sn_products(self, sn_lot):
        res = self.env['stock.move'].search_count([
            ('prescription_line_type', 'in', ['remove', 'recycle']),
            ('product_uom_qty', '=', 1),
            ('move_line_ids.lot_id', '=', sn_lot.id),
            ('state', '=', 'done'),
            ('location_dest_usage', '=', 'internal'),
        ])
        return super()._count_returned_sn_products(sn_lot) + res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    create_prescription = fields.Boolean('Create Prescription', help="Create a linked Prescription Order on Sale Order confirmation of this product.", groups='stock.group_stock_user')
