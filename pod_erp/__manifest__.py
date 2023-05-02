# -*- coding: utf-8 -*-
 

{

    "name": "Podiatry ERP",
    "version": "15.0.0.1",
    "category": "Podiatry",
    "summary": "Base for custom orthotics manufacturing",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://nwpodiatrtic.com",
    "description": """
""",

    "depends": [
        "account", 
        "account_accountant",
        "l10n_us",
        "base",
        "base_setup",
        "contacts", 
        "documents",
        "data_cleaning",
        "mrp",
        "product",
        "resource",
        "repair",
        "sale", 
        "sale_management", 
        "stock", 
        "sale_stock", 
     
        ],
    "data": [
        'security/practice_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/login_page.xml',
        'wizard/create_prescription_invoice_wizard.xml',
        'wizard/create_prescription_shipment_wizard.xml',
        'views/orthotic.xml',
        'views/device_route.xml',
        'views/prescription_order.xml',
        'views/directions.xml',
        'views/quant_unit.xml',
        'views/patient_details.xml',
        'views/pathology_category.xml',
        'views/pathology_group.xml',
        'views/pathology.xml',
        'views/patient_condition.xml',
        'views/patient_orthotic.xml',
        'views/patient_orthotic1.xml',
        'views/patient.xml',
        'views/patient_rounding.xml',
        'views/physician.xml',
        'views/prescription_line.xml',
        'views/res_partner.xml',
        'views/main_menu_file.xml',
        'report/report_view.xml',
        'report/patient_card_report.xml',
        'report/patient_conditions_document_report.xml',
        'report/patient_orthotics_document_report.xml',
        'report/prescription_demo_report.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "pod_erp/static/src/css/style.css",
        ],
 
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/icon.png"],

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
