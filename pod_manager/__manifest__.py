# -*- coding: utf-8 -*-


{

    "name": "Podiatry Manager",
    "version": "15.0.1.0",
    "summary": "",
    "category": "Industries",
    "description": """ """,
    # "sequence": -100,

    "depends": ["base", "sale_management", "stock", "account"],
    "data": [
        'security/podiatry_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/pod_role.xml',
        'views/assets.xml',
        'views/login_page.xml',
        'views/main_menu_file.xml',
        'wizard/create_rx_invoice_wizard.xml',
        'wizard/create_rx_shipment_wizard.xml',
        'views/pod_treatment.xml',
        'views/pod_rx_order.xml',
        'views/pod_rx_order_line.xml',
        'views/pod_pathology_category.xml',
        'views/pod_pathology_group.xml',
        'views/pod_pathology.xml',
        'views/pod_patient_condition.xml',
        'views/pod_patient_device.xml',
        'views/pod_patient_device1.xml',
        'views/pod_patient.xml',
        'views/pod_doctor.xml',
        "views/pod_role.xml",
        'views/res_partner.xml',
        'report/report_view.xml',
        'report/rx_demo_report.xml',
        'report/patient_card_report.xml',

    ],
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/Full logo.png"],
    "license": 'OPL-1',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
