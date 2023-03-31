# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Podiatry Dashboard',
    'version' : '0.1',
    'sequence': 200,
    'category': 'Human Resources/Podiatry',
    'website' : 'https://www.odoo.com/app/podiatry',
    'summary' : 'Dashboard for podiatry',
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
        'podiatry', 'web_dashboard'
    ],
    'data': [
        'views/podiatry_board_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'OEEL-1',
}
