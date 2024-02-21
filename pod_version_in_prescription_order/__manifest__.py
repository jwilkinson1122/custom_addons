
{
    'name': 'NWPL - Prescription Order Versions',
    'version': '17.0.0.0.0',
    'category': 'Prescriptions/Sales',
    'summary': 'For creating multiple prescription order versions',
    'description': 'For creating multiple prescription order versions',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'images': ['static/description/icon.png'],
    'depends': [
        'base', 
        'pod_prescription_management'
        ],
    'data': [
        'views/prescription_order.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
