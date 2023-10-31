
{
    'name': "Product Device Configurator - Sale",
    'version': '16.0.1.0.0',
    'summary': 'Device product configurator integration with sales',
    'license': 'LGPL-3',
    'author': "NWPL",
    'website': "https://nwpodiatric.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'sale',
        # oerp-odoo
        'product_device_configurator',
    ],
    'data': [
        'views/sale_order.xml',
        'wizards/device_configure_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
