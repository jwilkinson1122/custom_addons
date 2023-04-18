# -*- coding: utf-8 -*-
{
    'name': "Hospital Management System",

    'summary': "Hospital Management System",
    'sequence':3,

    'description': "Hospital Management System",

    'author': "My Company",
    'website': "https://codeclinic.ml",
    'application': True,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/create_appointment_wizard.xml',
        'views/patient.xml',
        'views/saleorder.xml',
        'views/parent.xml',
        'views/medicine.xml',
        'data/patient_seq.xml',
        'data/patient_mail_template.xml',
        'views/medicine_order.xml',
        'views/sale_medicine_invoice.xml',
        'views/kids.xml',
        'views/patient_gender.xml',
        'views/appointment.xml',
        'views/doctor.xml',
        'views/specialize.xml',
        'wizard/create_patient_report_wizard.xml',
        'report/report.xml',
        'report/patient_report_template.xml',
        'report/patient_report_wizard.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
