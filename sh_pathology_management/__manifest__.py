# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    'name': 'Pathology Lab Management System',
    'version': '16.0.1',
    'author': 'Softhealer Technologies',
    'category': 'Extra Tools',
    'website': 'www.softhealer.com',
    "support": "support@softhealer.com",
    "summary": "Pathology Lab Center Hospital Management Lab Test Medical Pathology Lab Business Pathology System Medical Management System Health Center Healthcare Management Clinic Management vaccination Patient Report Laboratory Test Labtest Odoo",
    "description": """Are you looking for comprehensive lab operations management plan? So you are at the right place. Our this module will help you to manage your lab with patients, technicians, pathologist, lab centers, collection centers, Also it will provide a feature to send the report on direct patients WhatsApp messenger. This module provides user-friendly views so it is easy to use for all users.""",
    'depends': ['account', 'mail', 'portal', 'utm'],
    'data': [

        'security/pathology_security.xml',
        'security/ir.model.access.csv',
        'report/sh_diagnosis_report_templates.xml',
        'data/ir_sequence_data.xml',
        'data/mail_data.xml',
        'views/sh_inherit_product_detail.xml',
        'views/sh_inherit_partner_detail.xml',
        'views/sh_lab_test_appointment_detail.xml',
        'views/sh_patient_diagnosis_views.xml',
        'views/sh_source_detail.xml',
        'views/sh_collection_detail.xml',
        'views/sh_laboratory_detail.xml',
        'views/sh_units_detail.xml',
        'views/sh_parameter_detail.xml',
        'views/sh_pre_information_detail.xml',
        'views/sh_sample_type_detail.xml',
        'views/sh_parameter_patient_detail.xml',
        'views/sh_pathology_portal_templtates.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "price": 80,
    "currency": "EUR"
}
