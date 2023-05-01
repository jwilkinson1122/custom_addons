# -*- coding: utf-8 -*-
{
    'name': "Podiatry Manager",
    'sequence': 1,
    'summary': """
        A podiatry practice management module.""",

    'description': """
        A podiatry practice management module for creating patient, doctor, 
        partner, medical test, and prescriptions.
    """,

    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",
    'category': 'Services',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'base_setup',
        'contacts',
        'website', 
        'website_sale', 
        'mail', 
        'account', 
        'account_accountant', 
        'l10n_us', 
        'sale', 
        'sale_management', 
        'stock', 
        'documents',
        'data_cleaning',
        'repair',
        
        
        ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/prescription_seq.xml',
        'wizard/create_prescription_view.xml',
        'wizard/prescription_report_view.xml',
        'views/patient_view.xml',
        'views/doctor_view.xml',
        'views/partner_view.xml',
        'views/prescription_view.xml',
        'views/medicaltest_view.xml',
        'views/website_patient_form.xml',
        'views/website_patient_view.xml',
        'views/website_prescription_form.xml',
        'views/orthotic_sale.xml',
        'views/sales_order.xml',
        'views/menu.xml',
        'reports/report.xml',
        'reports/sale_report_inherit.xml',
        'reports/prescription_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
