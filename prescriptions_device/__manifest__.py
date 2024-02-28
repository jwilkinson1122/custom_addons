# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescriptions - Device',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Device from prescriptions',
    'description': """Adds device data to prescriptions""",
    'author': "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['prescriptions', 'device'],
    'data': [
        'data/prescriptions_folder_data.xml',
        'data/prescriptions_facet_data.xml',
        'data/prescriptions_tag_data.xml',
        'data/prescriptions_workflow_rule_data.xml',
        'data/res_company_data.xml',
        'views/device_custom_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    # # 'auto_install': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
