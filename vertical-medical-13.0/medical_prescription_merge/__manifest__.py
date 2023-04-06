# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Prescription - Order Merge',
    'summary': 'Provides support for merging existing prescription orders',
    'version': '13.0.0.0.0',
    'category': 'Medical',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'GPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'medical_prescription',
    ],
    'data': [
        'wizards/medical_prescription_order_merge.xml',
    ],
}
