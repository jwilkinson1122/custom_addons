# -*- coding: utf-8 -*-
{
    'name': "Podiatry Practice",
    'sequence': 1,
    'summary': """
        A podiatry practice management module.""",

    'description': """
        A podiatry practice management module for creating patient, doctor and prescriptions.
    """,

    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",
    'category': 'Medical',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'website', 'website_sale', 'mail'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/prescription_seq.xml',
        'wizard/create_prescription_view.xml',
        'wizard/prescription_report_view.xml',
        'views/patient_view.xml',
        'views/doctor_view.xml',
        'views/department_view.xml',
        'views/prescription_view.xml',
        'views/medical_test_view.xml',
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
