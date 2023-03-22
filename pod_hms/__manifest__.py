# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

{

    "name": "Podiatry Medical Management System in Odoo",
    "version": "15.0.0.1",
    "summary": "Apps basic Hospital Management system Healthcare Management Clinic Management apps manage clinic manage Patient hospital manage Healthcare system Patient Management Hospital Management Healthcare Management Clinic Management hospital Lab Test Request",
    "category": "Industries",
    "description": """NWPL developed a new odoo/OpenERP module apps. This module is used to manage Hospital and Healthcare Management and Clinic Management apps. 
""",

    "depends": ["base", "product", "sale_management", "stock", "account"],
    "data": [
        'security/hospital_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        "data/stage_data.xml",
        'views/assets.xml',
        'views/login_page.xml',
        'wizard/create_prescription_invoice_wizard.xml',
        'wizard/create_prescription_shipment_wizard.xml',
        'views/medical_prescription_order.xml',
        'views/medical_prescription_line.xml',
        'views/medical_pathology_category.xml',
        'views/medical_pathology_group.xml',
        'views/medical_pathology.xml',
        'views/medical_patient_condition.xml',
        'views/medical_patient_device.xml',
        'views/medical_patient_device1.xml',
        'views/medical_patient.xml',
        'views/medical_practitioner.xml',
        "views/medical_practice.xml",
        'views/res_partner.xml',
        'report/report_view.xml',
        'report/patient_card_report.xml',
        'report/patient_conditions_document_report.xml',
        'report/patient_devices_document_report.xml',
        'report/prescription_demo_report.xml',
        "views/res_config_settings.xml",
        "wizard/change_prm_category.xml",
        "wizard/update_prm_attributes.xml",
        "wizard/update_prm_followers.xml",
        "wizard/update_prm_product_type.xml",
        "wizard/update_prm_price.xml",
        "wizard/update_prm_optional_products.xml",
        "wizard/copy_values_from_template.xml",
        "views/product_template.xml",
        'views/main_menu_file.xml',
        "data/data.xml",
        # "data/stage_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
                "pod_hms/static/src/js/product_kanbancontroller.js",
                "pod_hms/static/src/js/product_kanbanmodel.js",
                "pod_hms/static/src/js/product_kanbanrecord.js",
                "pod_hms/static/src/js/product_kanbanrender.js",
                "pod_hms/static/src/js/product_kanbanview.js",
                "pod_hms/static/src/css/styles.css"
        ],
        "web.assets_qweb": [
                "pod_hms/static/src/xml/*.xml"
        ]
    },
    "demo": [
        
    ],
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/Banner.gif"],
    "live_test_url": 'https://nwpodiatric.com',
    "license":'OPL-1',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
