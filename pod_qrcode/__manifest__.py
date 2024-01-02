# -*- coding: utf-8 -*-
{
    'name': 'NWPL QR Code Generator',
    'version': '17.0.0.0.0',
    'category': 'Extra Tools',
    'summary': 'Generate Unique QR Codes',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'base', 
        'sale', 
        'stock'
        ],
    'data': [
        'data/sequence.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'views/product_product_view.xml',
        'views/product_template_view.xml',
        'report/qrcode_template.xml',
        'report/paperformat.xml',
        'report/report_action.xml',
    ],
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'set_qr_code'
}
