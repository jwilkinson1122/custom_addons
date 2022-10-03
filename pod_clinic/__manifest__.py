# -*- coding: utf-8 -*-
{
    'name': "Podiatry Clinic",
    'summary': """
       Podiatry Clinic""",
    'description': """
        Long description of module's purpose
    """,
    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",
    'category': 'Medical',
    'sequence': 21,
    'depends': ['base', 'mail'],
    'data': [
        'security/pod_clinic_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizards/views/create_visitation.xml',
        'wizards/views/create_patient.xml',
        'wizards/views/create_service.xml',
        'views/practice.xml',
        'views/patient.xml',
        'views/prescription.xml',
        'views/visitation.xml',
        'views/service.xml',
        'views/doctor.xml',
        'views/item.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
