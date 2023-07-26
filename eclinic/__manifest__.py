# -*- coding: utf-8 -*-
{
    'name': "eclinic",

    'summary': """
        This module covers the common clinic cases
        Install and use it for your e-clinic system""",

    'description': """
        This module has common cases for you clinic, here are the features supported by this module:
        
        1. Master Data
        Clinic locations 
        Doctor/Practitioner
        Insurance
        Medicine
        Patient
        Pharmacist
        Staff
        Payment Method (In Progress)

        2. Transaction Data
        Appointments / Medical consultations
        Treatment Plans (Outpatient and Inpatient) (on develop, will updated soon)
        Prescription orders

        3. Reports (on develop, while waiting you can make your own template)
        Doctor Appointments Report 
        Medical history       
        Patient Appointments Report        
        Patient Billing Report
        Revenue Report
    """,

    'author': "Codesev",
    'website': "https://codesev.com/",

    'category': 'Health',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        # Sequences
        'sequences/transaction.xml',

        # Views
        'views/clinic.xml', # this should come before all the other menu (contain parent menu)
        'views/appointment.xml',
        'views/doctor.xml',
        'views/insurance.xml',
        'views/insurance_policy.xml',
        'views/medicine.xml',
        'views/patient.xml',
        'views/pharmacist.xml',
        'views/staff.xml',
        'views/transaction.xml',

        # Reports
        'reports/appointment.xml',
        'reports/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/staff.xml',
        'demo/medicine.xml',
        'demo/insurance.xml',
        'demo/pharmacy.xml',
        'demo/patient.xml',
        'demo/doctor.xml',
        'demo/appointment.xml',
        'demo/clinic.xml',
    ],
    'application': True,
    'installable': True,
    'currency': 'usd',
    'price': 0,
    'license': 'LGPL-3',
    'images': [
        'static/description/icon.png',
    ],
}
