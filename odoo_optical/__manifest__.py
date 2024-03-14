# -*- coding: utf-8 -*-

{
    'name': 'Optical / Eye Clinic Solution',
    'version': '17.0.0.0.0',
    'summary': """Optical / Eye Clinic Solution""",
    'description': """Optical / Eye Clinic Solution""",
    'category': 'Optical',
    'author': 'bisolv',
    'website': "",
    'license': 'AGPL-3',

    'price': 15.0,
    'currency': 'USD',

    'depends': ['base', "sale_management", "hr", "sales_team",

                'report_utils2'


                ],

    'data': [
        'security/ir.model.access.csv',
        'data/hr_job.xml',
        'data/reports.xml',
        'views/hr_job_view.xml',
        'views/hr_employee_view.xml',
        'views/sale_order_view.xml',
        'views/config.xml',
        'report/report_optical_prescription.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
