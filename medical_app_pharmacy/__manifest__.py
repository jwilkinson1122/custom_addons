# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    'name': 'Medical Apps - Pharmacy',
    'version': '13.0.0.0.0',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'category': 'Medical',
    'website': 'https://laslabs.com',
    'license': 'GPL-3',
    'application': True,
    'installable': True,
    'depends': [
        'medical_insurance',
        'medical_medicament_storage',
        'medical_prescription_disease_state',
        'medical_prescription_merge',
        'medical_prescription_state',
        'sale_crm_medical_prescription',
        'sale_stock_medical_prescription',
    ],
    'data': [
        'templates/assets.xml',
        'views/medical_app_pharmacy_menu.xml',
    ],
}
