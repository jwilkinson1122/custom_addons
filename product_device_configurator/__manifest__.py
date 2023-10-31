{
    'name': "Product Device Configurator",
    'version': '16.0.1.1.0',
    'summary': 'Base device product configurator module',
    'license': 'LGPL-3',
    'author': "NWPL",
    'website': "https://nwpodiatric.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'security/product_device_configurator_groups.xml',
        'security/ir.model.access.csv',
        'security/device_design_security.xml',
        'security/device_die_security.xml',
        'security/device_difficulty_security.xml',
        'security/device_finishing_security.xml',
        'security/device_material_security.xml',
        'security/device_pricelist_security.xml',
        'data/decimal_precision.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'views/device_pricelist.xml',
        'views/device_design.xml',
        'views/device_die.xml',
        'views/device_difficulty.xml',
        'views/device_finishing.xml',
        'views/device_material.xml',
        'views/menus.xml',
        'wizards/device_configure_views.xml',
    ],
    'application': True,
    'installable': True,
}
