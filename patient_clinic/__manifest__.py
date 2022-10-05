# -*- coding: utf-8 -*-
{
    'name': "Patient Clinic",
    'summary': """
       Patient Clinic""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Jangakniat",
    'website': "http://www.ubig.co.id",
    'category': 'Patient Clinic System',
    'sequence': 21,
    'depends': ['base', 'mail'],
    'data': [
        'security/patient_clinic_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizards/views/create_visitation.xml',
        'wizards/views/create_patient.xml',
        'wizards/views/create_service.xml',
        'views/doctor.xml',
        'views/patient.xml',
        'views/prescription.xml',
        'views/visitation.xml',
        'views/type.xml',
        'views/service.xml',
        'views/item.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
