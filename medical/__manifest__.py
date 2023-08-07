# -*- coding: utf-8 -*-
# Copyright 2016-2018 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Odoo Medical',
    'version': '13.0.0.0.0',
    'category': 'Medical',
    'depends': [
        'base', 
        'base_setup', 
        'contacts', 
        'sale_management', 
        'account', 
        'l10n_us', 
        'stock', 
        'product', 
        # 'product_configurator',
        # 'product_configurator_sale',
        # 'product_configurator_mrp',
        # 'product_configurator_sale_mrp',
        # 'product_configurator_mrp_component',
        # 'product_configurator_purchase',
        'mail',
        
    ],
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'license': 'GPL-3',
    'data': [
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        # 'templates/assets.xml',
        'views/medical_abstract_entity.xml',
        'views/medical_patient.xml',
        'views/res_partner.xml',
        'views/medical_menu.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "medical/static/src/js/medical.tour.js",
        ],
        'web.assets_qweb': [
        ],
    },
    'demo': [
        'demo/medical_patient_demo.xml',
    ],
    'installable': True,
    'application': True,
}
