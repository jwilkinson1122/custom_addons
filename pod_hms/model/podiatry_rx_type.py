# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
# classes under cofigration menu of laboratry


class podiatry_rx_type(models.Model):

    _name = 'podiatry.rx_type'
    _description = 'podiatry test type'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    criteria_ids = fields.One2many(
        'podiatry_rx.criteria', 'rx_id', 'Critearea')
    podiatry_product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    info = fields.Text('Extra Information')
