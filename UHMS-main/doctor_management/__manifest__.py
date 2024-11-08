# __manifest__.py
{
    'name': "Doctor Management",
    'version': '1.0',
    'summary': "Manage doctors and their schedules independently",
    'author': "Your Name",
    'category': 'Healthcare',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/doctor_views.xml',
        'views/specialization_views.xml',
        'views/schedule_views.xml',
        'views/doctor_menus.xml',
    ],
    'installable': True,
    'application': True,
}
