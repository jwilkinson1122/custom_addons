# -*- coding: utf-8 -*-

{
    'name': 'NWPL - Product Size Matrix on Sales Order',
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
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'pod_prescription_management', 
        'pod_prescription_stock',
        'sale_management', 
        'stock', 
        'account',
        ],
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
    "images":['static/description/icon.png'],
}
