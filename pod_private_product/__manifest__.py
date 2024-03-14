{
    'name': "NWPL - Partner Products",
    'summary': """Product Preferences for Customers""",
    'description': """
        Create a relation between a product and a customer.
    """,
    'author': "NWPL",
    'website': "https://www.nwpodiatric.com",
    'version': '17.0.0.0.0',
    'license': 'AGPL-3',
    'category': 'Inventory',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'views/product_template.xml',
        'views/product_variant_view.xml',
        'views/res_partner.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
