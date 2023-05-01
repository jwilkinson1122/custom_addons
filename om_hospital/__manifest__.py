# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hospital Management Software',
    'version': '1.0',
    'author': 'Tuấn Cris',
    'summary': 'Hospital Management Software',
    'sequence': -100,
    'description': """ Hospital Management Software """,
    'category': 'Productivity',
    'depends': ['base',
                'mail',
                'report_xlsx',
                ],
    'data': [
        # orders security => data => wizard => views => report
        # menu wizard add in the view files
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/create_prescription_view.xml',
        'wizard/prescription_report_view.xml',
        'views/doctor_view.xml',
        'views/prescription_view.xml',
        'views/patient_all.xml',
        'views/patient_kids.xml',
    
        # 'views/sale.xml',
        # 'views/product.xml',
        'report/report_patient_details.xml',
        'report/report_prescription_medicine_details.xml',
        'report/report.xml',
        'report/report_patient_prescriptions.xml',
    ],
    'demo': [],
    'qweb': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
