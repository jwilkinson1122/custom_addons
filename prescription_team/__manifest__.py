# -*- coding: utf-8 -*-


{
    'name': 'NWPL Prescription Teams',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Prescription',
    'summary': 'Prescription Teams',
    'description': """
Using this application you can manage Prescription Teams with CRM and/or Prescription
=======================================================================
 """,
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
            'prescription_team/static/**/*',
        ],
    },
    'license': 'LGPL-3',
}
