# -*- coding: utf-8 -*-
{
    'name': "Syn Hospital Management",
    'version': "15.0.1.0.0",
    'summary': "Hospital Management with patient,appointment,medicine info",

    'description': "Hospital Management",

    'author': "PSS",
    'website': "https://prefortune.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tutorials',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['mail'],
    # always loaded
    'data': [
         'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/sequence_data.xml',
        'wizard/cancel_appointment_view.xml',
        'views/menu.xml',
        'views/patient_view.xml',
        'views/appointment_view.xml',
        'views/medicine_view.xml',
    ],
    'sequence': -50,
    'images' : ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    # only loaded in demonstration mode
    'demo': [],
}
