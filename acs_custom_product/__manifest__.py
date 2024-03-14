
{
    'name':'Product - ACS',
    'category': 'Products',
    'version': '17.0.0.0.0',
    'author': 'Odoo',
    'maintainer': 'Odoo',
    'website': 'odoo.com',
    'license': 'Other proprietary',
    'depends': ['stock', 'sale', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/product_configuration_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
