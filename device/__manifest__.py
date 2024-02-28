# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Device',
    'version' : '0.1',
    'sequence': 185,
    'category': 'Orthtoic Device',
    'website' : 'https://www.odoo.com/app/device',
    'summary' : 'Manage your device and track orthotic costs',
    'description' : """Add custom options to your device. Show all costs associated to a custom device.""",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/device_security.xml',
        'security/ir.model.access.csv',
        'views/device_custom_model_views.xml',
        'views/device_custom_views.xml',
        'views/device_custom_cost_views.xml',
        'views/device_board_view.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'data/device_orthotics_data.xml',
        'data/device_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/mail_activity_type_data.xml',
    ],

    'demo': [
        # 'data/device_demo.xml',
        ],

    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'device/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
