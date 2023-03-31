# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Podiatry',
    'version' : '0.1',
    'sequence': 185,
    'category': 'Human Resources/Podiatry',
    'website' : 'https://www.odoo.com/app/podiatry',
    'summary' : 'Manage your podiatry and track device costs',
    'description' : """
Device, leasing, insurances, cost
==================================
With this module, Odoo helps you managing all your devices, the
prescriptions associated to those device as well as services, costs
and many other features necessary to the management of your podiatry
of device(s)

Main Features
-------------
* Add devices to your podiatry
* Manage prescriptions for devices
* Reminder when a prescription reach its expiration date
* Add services, laterality values for all devices
* Show all costs associated to a device or to a type of service
* Analysis graph for costs
""",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/podiatry_security.xml',
        'security/ir.model.access.csv',
        'views/podiatry_device_model_views.xml',
        'views/podiatry_device_views.xml',
        'views/podiatry_device_cost_views.xml',
        'views/podiatry_board_view.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'data/podiatry_devices_data.xml',
        'data/podiatry_data.xml',
        'data/mail_data.xml',
    ],

    'demo': ['data/podiatry_demo.xml'],

    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'podiatry/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
