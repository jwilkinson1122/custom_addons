# -*- coding : utf-8 -*-

{
	'name': 'NWPL - Customer Reorder Sale',
	'version': '17.0.0.0.0',
	'category': 'Sales',
	'summary': 'Reordering Previous Order',
	'description': """ Customer Reorder Sale.""",
	'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
	'depends': ['base','sale','sale_management'],
	'data': ['views/res_partner.xml'],
	'license': 'LGPL-3',
	'installable': True,
    'auto_install': False,
    "images":['static/description/icon.png'],
}
