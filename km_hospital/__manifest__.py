# -*- coding: utf-8 -*-
{
    'name': "KM Hospital",
    'sequence': 1,
    'summary': """
        A hospital management module.""",

    'description': """
        A hospital management module for creating patient, doctor, 
        department, medical test, and appointments.
    """,

    'author': "Kamrul & Niazi",
    'website': "http://www.yourcompany.com",
    'category': 'Services',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_setup', 
        'hr', 
        'website', 
        'website_sale', 
        'mail', 
        'sale_management', 
        'sale', 
        'product', 
        'stock', 
        'sale_stock', 
        'account',
        'account_accountant',
        'l10n_us',
        'mrp',
        'repair',
        'documents'
        ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        "views/res_config_settings_view.xml",
        'data/appointment_seq.xml',
        "data/menu_configurable_product.xml",
        "data/product_attribute.xml",
        "data/ir_sequence_data.xml",
        "data/ir_config_parameter_data.xml",
        "views/product_view.xml",
        "views/product_attribute_view.xml",
        "views/product_config_view.xml",
        'views/patient_view.xml',
        'views/doctor_view.xml',
        'views/department_view.xml',
        'views/appointment_view.xml',
        'views/medicaltest_view.xml',
        'views/website_patient_form.xml',
        'views/website_patient_view.xml',
        'views/website_apntment_form.xml',
        'views/equipment_sale.xml',
        'views/sales_order.xml',
        'reports/report.xml',
        'reports/sale_report_inherit.xml',
        'reports/appointment_report.xml',
        "wizard/product_configurator_view.xml",
        'wizard/create_appointment_view.xml',
        'wizard/appointment_report_view.xml',
    ],
     "assets": {
        "web.assets_backend": [
            "/km_hospital/static/scss/form_widget.scss",
            "/km_hospital/static/js/form_widgets.js",
            "/km_hospital/static/js/data_manager.js",
            "/km_hospital/static/js/relational_fields.js",
        ]
    },
    "demo": [
        "demo/res_partner_demo.xml",
        "demo/product_template.xml",
        "demo/product_attribute.xml",
        "demo/product_config_domain.xml",
        "demo/product_config_lines.xml",
        "demo/product_config_step.xml",
        "demo/config_image_ids.xml",
    ],
    "post_init_hook": "post_init_hook",
    "qweb": ["static/xml/create_button.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
    "external_dependencies": {"python": ["mako"]},
}
