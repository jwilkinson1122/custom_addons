{
    'name': "Product Device Configurator - Sale CRM",
    'version': '16.0.1.0.0',
    'summary': 'Device product configurator integration with sales and CRM',
    'license': 'LGPL-3',
    'author': "NWPL",
    'website': "https://nwpodiatric.com",
    'category': 'Sales/CRM',
    'depends': [
        # odoo
        'sale_crm',
        # oerp-odoo
        'product_device_configurator_sale',
    ],
    'installable': True,
    'auto_install': True,
}
