{
    'name': 'NWPL Contacts Extended',
    'version': '17.0.0.0.0',
    'author': 'NWPL',
    'website': 'https://nwpodiatric.com',
    'license': 'LGPL-3',
    'category': 'Podiatry/Contacts',
    'summary': 'Add the field is a parent company to the partner object',
    'depends': [
        'pod_prescriptions_contact'
        ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
