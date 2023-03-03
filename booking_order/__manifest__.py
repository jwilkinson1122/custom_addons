# -*- coding: utf-8 -*-
{
    'name': "Booking Order",

    'summary': """
        Booking Order NWPL""",

    'description': """
        Booking Order NWPL
    """,

    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        "base_setup",
        "resource",
        'sale', 
        'sale_management', 
        'sale_stock',
        'stock',
        'product', 
        'contacts', 
        'mail',
        "account",
        "account_accountant",
        "mail",
        'purchase',
        ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        "views/res_config_settings_view.xml",
        "data/product_attribute.xml",
        "data/ir_sequence_data.xml",
        "data/ir_config_parameter_data.xml",
        'views/service_team_views.xml',
        'views/templates.xml',
        'wizard/wizard_cancelled.xml',
        'views/work_order_views.xml',
        'views/booking_order_views.xml',
        "views/patient.xml",
        "views/practice.xml",
        "views/practitioner.xml",
        "views/product_view.xml",
        "views/product_attribute_view.xml",
        "views/product_config_view.xml",
        "views/actions.xml",
        'views/menu.xml',
        # "views/partner.xml",
        'report/report_work_order.xml',
        'report/report.xml',
        'data/data.xml',
        # 'wizard/wizard_cancelled.xml',
        "wizard/product_configurator_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/booking_order/static/scss/form_widget.scss",
            "/booking_order/static/js/form_widgets.js",
            "/booking_order/static/js/data_manager.js",
            "/booking_order/static/js/relational_fields.js",
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
        "demo/product_template.xml",
        "demo/product_attribute.xml",
        "demo/product_config_domain.xml",
        "demo/product_config_lines.xml",
        "demo/product_config_step.xml",
        "demo/config_image_ids.xml",
    ],
    "images": ["static/description/icon.png"],
    "post_init_hook": "post_init_hook",
    "qweb": ["static/xml/create_button.xml"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "external_dependencies": {"python": ["mako"]},
}
