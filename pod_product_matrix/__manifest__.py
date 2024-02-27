# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Size Matrix on Sales Order',
    'version': '17.0.0.0.0',
    'category': 'Sales',
    'summary': 'Sales Product Size Matrix on Sale order Product Size Matrix Sale Product Size Matrix product attribute size matrix product variant size matrix product textile size matrix product foot ware size matrix product color size matrix product variants size matrix',
    'description': """
        
        Product Size Matrix in odoo,
        Product Attributes in odoo,
        Product Variant Sizing in odoo,
        Update Variants Price in odoo,
        Add Product Matrix in odoo,
        Increse/Decrease Product Qty in odoo,

    """,
    'author': 'BrowseInfo',
    "price": 99,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.com',
    'depends': ['sale_management', 'stock', 'account'],
    'data': [
        'security/product_sm_group.xml',
        'security/ir.model.access.csv',
        'data/product_sm_demo.xml',
        'wizard/matrix_wizard.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/zFRuRZfGhmE',
    "images":['static/description/Banner.gif'],
}
