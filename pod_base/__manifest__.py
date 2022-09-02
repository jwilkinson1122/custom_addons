

{
    'name': 'NWPL',
    'description': '''Adds Pod Abstract Entity for Podiatry''',
    'version': '15.0.0.0.1',
    'category': 'Medical',
    'depends': [
        'base',
        'product',
        'base_locale_uom_default',
    ],
    'author': 'NWPL',
    'website': 'http://nwpodiatric.com',
    #    'license': 'GPL-3',
    'data': [
        'data/ir_sequence_data.xml',
        'data/pod_specialty.xml',
        'security/pod_security.xml',
        'security/ir.model.access.csv',
        # 'templates/assets.xml',
        'views/res_partner.xml',
        'views/pod_abstract_entity.xml',
        'views/pod_patient.xml',
        'views/pod_menu.xml',
        'views/pod_specialty.xml',
    ],
    'demo': [
        # 'demo/pod_patient_demo.xml',
    ],
    'installable': True,
    'application': True,
}
