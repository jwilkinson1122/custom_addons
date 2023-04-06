# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Medicament - Reusable Storage Instructions',
    'summary': 'Makes storage instructions into reusable entities',
    'version': '13.0.0.0.0',
    'category': 'Medical',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'GPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'medical_medicament',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/medical_medicament.xml',
        'views/medical_medicament_storage.xml',
    ],
    'demo': [
        'demo/medical_medicament_storage.xml',
        'demo/medical_medicament.xml',
    ],
}
