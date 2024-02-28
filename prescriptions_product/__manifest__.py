# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescriptions - Product',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Products from Prescriptions',
    'description': """
Adds the ability to create products from the prescription module and adds the
option to send products' attachments to the prescriptions app.
""",
    'author': "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['prescriptions', 'product'],
    'data': [
        'data/prescriptions_folder_data.xml',
        'data/prescriptions_facet_data.xml',
        'data/prescriptions_tag_data.xml',
        'data/res_company_data.xml',
        'views/res_config_settings_views.xml',
        'views/prescriptions_prescription_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    # 'auto_install': False,
    'license': 'LGPL-3',
}
