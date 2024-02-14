# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescription Teams',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Prescription',
    'summary': 'Prescription Teams',
    'description': """Manage Prescription Teams with CRM and Prescription.""",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/prescription_team_security.xml',
        'security/ir.model.access.csv',
        'data/crm_team_data.xml',
        'views/crm_tag_views.xml',
        'views/crm_team_views.xml',
        'views/crm_team_member_views.xml',
        'views/mail_activity_views.xml',
        'views/res_partner_views.xml',
        ],
    'demo': [
        'data/crm_team_demo.xml',
        'data/crm_tag_demo.xml',
    ],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'pod_prescription_team/static/**/*',
        ],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
}
