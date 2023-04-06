# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Prescription Verification - States and Logic',
    'summary': 'Introduces verified prescription states and related logic',
    'version': '13.0.0.0.0',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'category': 'Medical',
    'website': 'https://laslabs.com',
    'license': 'GPL-3',
    'installable': True,
    'auto_install': False,
    'depends': [
        'medical_prescription_state',
    ],
    'data': [
        'data/base_kanban_stage.xml',
    ],
    'demo': [
        'demo/medical_medicament.xml',
        'demo/medical_patient.xml',
        'demo/medical_patient_medication.xml',
        'demo/medical_physician.xml',
        'demo/medical_prescription_order.xml',
        'demo/medical_prescription_order_line.xml',
    ]
}
