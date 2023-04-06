# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Appointment',
    'summary': 'Add Appointment concept to medical_physician',
    'version': '13.0.0.0.0',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'category': 'Medical',
    'depends': [
        'auditlog',
        'mail',
        'medical_physician',
    ],
    'data': [
        'views/medical_appointment_view.xml',
        'views/medical_menu.xml',
        'views/medical_patient.xml',
        'security/ir.model.access.csv',
        # 'security/medical_security.xml',
        'data/auditlog_rule.xml',
        'data/decimal_precision_data.xml',
        'data/medical_appointment_data.xml',
        'data/medical_appointment_sequence.xml',
    ],
    'website': 'https://laslabs.com',
    'licence': 'GPL-3',
    'installable': True,
    'auto_install': False,
}
