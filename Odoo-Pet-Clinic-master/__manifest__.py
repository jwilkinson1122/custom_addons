# -*- coding: utf-8 -*-
{
    'name': "Pet Clinic",
    'summary': """
       Pet Clinic""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Jangakniat",
    'website': "http://www.ubig.co.id",
    'category': 'Pet Clinic System',
    'sequence': 21,
    'depends': ['base', 'mail'],
    'data': [
        'security/pet_clinic_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizards/views/create_visitation.xml',
        'wizards/views/create_pet.xml',
        'wizards/views/create_service.xml',
        'views/client.xml',
        'views/pet.xml',
        'views/appointment.xml',
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
