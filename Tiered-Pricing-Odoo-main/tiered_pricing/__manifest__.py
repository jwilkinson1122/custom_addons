{
    'name': 'Tiered Pricing',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds tiered pricing option to the product pricelist items.',
    'description': """
        This module adds a tiered pricing option to the product pricelist items.
    """,
    'author': 'Nikhil',
    'depends': ['product', 'sale'],
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
    'application': False,
}

