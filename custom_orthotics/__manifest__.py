# -*- coding: utf-8 -*-
{
    'name': "NWPL",
    'summary': """
       Custom Orthotics Manufacturing """,
    'description': """
        Long description of module's purpose
    """,
    'author': "NWPL",
    'website': "http://www.nwpodiatry",
    'category': 'Medical Device Manufacturing',
    'sequence': 21,
    'depends': ['base', 'mail'],
    'data': [
        'security/custom_orthotics_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizards/views/create_order.xml',
        'wizards/views/create_patient.xml',
        'wizards/views/create_service.xml',
        'views/doctor.xml',
        'views/patient.xml',
        'views/prescription.xml',
        'views/order.xml',
        'views/service.xml',
        'views/practice.xml',
        'views/item.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
