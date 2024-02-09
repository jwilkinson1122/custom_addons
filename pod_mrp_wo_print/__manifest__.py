# -*- coding: utf-8 -*-

{
    'name': 'Print Work Order Details',
    'summary': """Generate PDF Report of Work Order""",
    'summary': """Generate PDF Report of Work Order""",
    'version': '17.0.0.0.0',
    'author': 'NWPL',
    'website': "https://www.nwpodiatric.com/",
    'category': 'Manufacturing',
    'depends': ['mrp'],
    'license': 'AGPL-3',
    'data': [
        'views/report_work_order.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
