{
    'name': 'NWPL Prescriptions Partner',
    'version': '17.0.0.0.0',
    'summary': 'Manage the contacts of a podiatry practice.',
    'description': """
        Adds the notion of practices, practitioners, and patients.""",
    'category': 'Services/Medical',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'license': 'LGPL-3',
    'depends': [
        'portal', 
        'contacts'
        ],
    'data': [
        'security/prescriptions_partner_groups.xml',
        'security/ir.model.access.csv',
        'security/prescriptions_partner_rules.xml',
        'views/prescriptions_partner_views.xml',
        'views/prescriptions_partner_menus.xml',
        'views/prescriptions_patient_views.xml',
        'views/prescriptions_partner_portal_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': ['data/demo/prescriptions_partner_demo_data.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
