

{
    'name': "Northwest Podiatric Practiceoratory",
    'summary': """
        Northwest Podiatric Practiceoratory Module
    """,
    'description': """
        Northwest Podiatric Practiceoratory Module 
        for remote Clinic Practiceoratories Management
    """,
    'author': "NWPL",
    'website': "https://nwpodiatric.com",
    'category': 'Medical',
    'version': '15.0.0.0.1',
    'depends': ['base', 'mail', 'product', 'contacts'],
    'data': [
        'views/pod_menu.xml',
        'views/pod_patient.xml',
        'views/medical_center.xml',
        'views/pod_practice_view.xml',
        'data/pod_practice_sequences.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
