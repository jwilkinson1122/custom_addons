# -*- coding: utf-8 -*-
{
    'name': "Podiatry HMS",
    'sequence': 1,
    'summary': """
        A podiatry management module.""",

    'description': """
        A podiatry management module for creating patient, doctor, and prescriptions.
    """,

    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",
    'category': 'Services',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_sale', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/prescription_seq.xml',
        'wizard/create_prescription_view.xml',
        'wizard/prescription_report_view.xml',
        'wizard/doctor_wizard.xml',
        'views/patient_view.xml',
        'views/doctor_view.xml',
        'views/prescription_view.xml',
        'views/podtest_view.xml',
        'views/website_patient_form.xml',
        'views/website_patient_view.xml',
        'views/website_prescription_form.xml',
        'views/device_sale.xml',
        'views/sales_order.xml',
        'reports/report.xml',
        'reports/sale_report_inherit.xml',
        'reports/prescription_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
