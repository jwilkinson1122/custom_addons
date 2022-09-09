# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
# classes under cofigration menu of laboratry


class podiatry_test_type(models.Model):

    _name = 'podiatry.test_type'
    _description = 'podiatry test type'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    critearea_ids = fields.One2many(
        'podiatry_test.critearea', 'test_id', 'Critearea')
    service_product_id = fields.Many2one(
        'product.product', 'Service', required=True)
    info = fields.Text('Extra Information')
