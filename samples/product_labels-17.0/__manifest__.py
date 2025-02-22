# -*- coding: utf-8 -*-
{
    'name': "Custom Product Label",
    'description' : """
        Custom module to print label for products and variants
    """,
    'category': 'Barcode',
    'author' : "Normand Terceros",
    'website' : "https://normand.dev",
    'depends' : ['product','mail'],
    'data': [
        'security/ir.model.access.csv',
        'report/product_label_report.xml',
        'wizard/product_label_view.xml'
    ]
}