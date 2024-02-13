# -*- coding: utf-8 -*-



{
    'name': 'NWPL - Prescriptions Base',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Prescriptions',
    'summary': 'Prescriptions internal machinery',
    'description': """This module contains all the features of Prescriptions Management.""",
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'knowledge',
        'pos_sale',
        'purchase_stock',
        'sale',
        'sale_management',
        'sale_product_matrix',
        'sale_product_configurator',
        'sale_purchase',
        'website_sale_comparison',
        # 'website_sale_loyalty',
        'website_sale_product_configurator',
        'website_sale_stock',
        # 'website_sale_wishlist',
        'pod_prescriptions_contacts',
        'pod_prescriptions_team',
        'account_payment',  # -> account, payment, portal
        'utm',
        'theme_orchid',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/ir_rules.xml',

        'report/account_invoice_report_views.xml',
        'report/ir_actions_report_templates.xml',
        'report/ir_actions_report.xml',
        'report/prescriptions_report_views.xml',

        'data/ir_cron.xml',
        'data/ir_sequence_data.xml',
        'data/prescriptions_stage_data.xml',
        'data/mail_activity_type_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/mail_template_data.xml',
        'data/ir_config_parameter.xml', # Needs mail_template_data
        'data/onboarding_data.xml',
        # 'data/pos_config.xml',
        'data/res_config_settings.xml',
        'data/product_public_category.xml',
        'data/product_category.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template.xml',
        'data/product_template_attribute_line.xml',
        'data/product_product.xml',
        'data/product_image.xml',
        # 'data/knowledge_article.xml',

        'wizard/account_accrued_orders_wizard_views.xml',
        'wizard/mass_cancel_orders_views.xml',
        'wizard/payment_link_wizard_views.xml',
        'wizard/res_config_settings_views.xml',
        'wizard/prescriptions_make_invoice_advance_views.xml',
        'wizard/prescriptions_order_cancel_views.xml',
        'wizard/prescriptions_order_discount_views.xml',

        # Define prescriptions order views before their references
        'views/prescriptions_order_views.xml',
        'views/prescriptions_order_kanban_view.xml',
        'views/sale_order_view.xml',
        'views/account_views.xml',
        'views/crm_team_views.xml',
        'views/mail_activity_views.xml',
        'views/mail_activity_plan_views.xml',
        'views/payment_views.xml',
        'views/product_document_views.xml',
        'views/product_packaging_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/prescriptions_order_line_views.xml',
        'views/prescriptions_portal_templates.xml',
        'views/utm_campaign_views.xml',

        'views/prescriptions_menus.xml',  # Last because referencing actions defined in previous files
    ],
    'demo': [
        'data/product_demo.xml',
        'data/prescriptions_demo.xml',
        'demo/website.xml',
        'demo/website_attachments.xml',
        'demo/website_page_views.xml',
        'demo/website_theme_apply.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_prescriptions/static/src/scss/prescriptions_onboarding.scss',
            'pod_prescriptions/static/src/js/prescriptions_progressbar_field.js',
            'pod_prescriptions/static/src/js/tours/prescriptions.js',
            'pod_prescriptions/static/src/js/prescriptions_product_field.js',
            'pod_prescriptions/static/src/xml/**/*',
        ],
        'web.assets_frontend': [
            'pod_prescriptions/static/src/scss/prescriptions_portal.scss',
            'pod_prescriptions/static/src/js/prescriptions_portal_sidebar.js',
            'pod_prescriptions/static/src/js/prescriptions_portal_prepayment.js',
            'pod_prescriptions/static/src/js/prescriptions_portal.js',
        ],
        'web.assets_tests': [
            'pod_prescriptions/static/tests/tours/**/*',
        ],
        'web.qunit_suite_tests': [
            'pod_prescriptions/static/tests/**/*',
            ('remove', 'pod_prescriptions/static/tests/tours/**/*')
        ],
        'web.report_assets_common': [
            'pod_prescriptions/static/src/scss/prescriptions_report.scss',
        ],
    },
    'installable': True,
    'post_init_hook': '_synchronize_cron',
    'license': 'LGPL-3',
}
