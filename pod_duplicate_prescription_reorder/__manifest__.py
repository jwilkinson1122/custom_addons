# -*- coding : utf-8 -*-

{
	'name': 'Prescription Order History | Customer Reorder Prescription',
	'version': '17.0.0.0',
	'category': 'Prescriptions',
	'summary': 'Repeat Prescription Order Reordering Previous Order',
	'description': """ Customer Reorder Prescription.""",
	'author': 'NWPL',
    'website': 'https://www.nwpodiatric',
	'depends': [
        'base',
        'pod_prescription',
        'pod_prescription_management'],
	'data': ['views/res_partner.xml'],
	'license': 'LGPL-3',
	'installable': True,
    'auto_install': False,
    "images":['static/description/icon.png'],
}
