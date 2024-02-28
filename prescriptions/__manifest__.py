# -*- coding: utf-8 -*-
{
    'name': "NWPL - Prescriptions",
    'summary': "Prescriptions Management",
    'description': """App to upload and manage prescriptions.""",
    'author': "NWPL",
    'category': 'Medical/Prescriptions',
    'sequence': 10,
    'version': '17.0.0.0.0',
    'application': True,
    'website': 'https://www.nwpodiatric.com',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'mail', 
        'portal', 
        'web_enterprise', 
        'attachment_indexation', 
        'digest'
        ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/digest_data.xml',
        'data/mail_template_data.xml',
        'data/mail_activity_type_data.xml',
        'data/prescriptions_folder_data.xml',
        'data/prescriptions_facet_data.xml',
        'data/prescriptions_tag_data.xml',
        'data/prescriptions_share_data.xml',
        'data/prescriptions_prescription_data.xml',
        'data/prescriptions_workflow_data.xml',
        'data/ir_asset_data.xml',
        'data/ir_config_parameter_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/prescriptions_prescription_views.xml',
        'views/prescriptions_facet_views.xml',
        'views/prescriptions_folder_views.xml',
        'views/prescriptions_share_views.xml',
        'views/prescriptions_tag_views.xml',
        'views/prescriptions_workflow_action_views.xml',
        'views/prescriptions_workflow_rule_views.xml',
        'views/mail_activity_views.xml',
        'views/mail_activity_plan_views.xml',
        'views/prescriptions_menu_views.xml',
        'views/prescriptions_templates_share.xml',
        'wizard/prescriptions_link_to_record_wizard_views.xml',
        'wizard/prescriptions_request_wizard_views.xml',
    ],

    'demo': [
        'demo/prescriptions_folder_demo.xml',
        'demo/prescriptions_prescription_demo.xml',
    ],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'prescriptions/static/src/scss/prescriptions_views.scss',
            'prescriptions/static/src/scss/prescriptions_kanban_view.scss',
            'prescriptions/static/src/attachments/**/*',
            'prescriptions/static/src/core/**/*',
            'prescriptions/static/src/js/**/*',
            'prescriptions/static/src/owl/**/*',
            'prescriptions/static/src/views/**/*',
            'prescriptions/static/src/web/**/*',
        ],
        'web._assets_primary_variables': [
            'prescriptions/static/src/scss/prescriptions.variables.scss',
        ],
        "web.dark_mode_variables": [
            ('before', 'prescriptions/static/src/scss/prescriptions.variables.scss', 'prescriptions/static/src/scss/prescriptions.variables.dark.scss'),
        ],
        'prescriptions.public_page_assets': [
            ('include', 'web._assets_helpers'),
            ('include', 'web._assets_backend_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap_backend'),
            'prescriptions/static/src/scss/prescriptions_public_pages.scss',
        ],
        'prescriptions.pdf_js_assets': [
            ('include', 'web.pdf_js_lib'),
        ],
        'web.tests_assets': [
            'prescriptions/static/tests/helpers/**/*',
        ],
        'web.assets_tests': [
            'prescriptions/static/tests/tours/*',
        ],
        'web.qunit_suite_tests': [
            'prescriptions/static/tests/**/*',
            ('remove', 'prescriptions/static/tests/**/*mobile_tests.js'),
            ('remove', 'prescriptions/static/tests/helpers/**/*'),
            ('remove', 'prescriptions/static/tests/tours/*'),
        ],
        'web.qunit_mobile_suite_tests': [
            'prescriptions/static/tests/prescriptions_test_utils.js',
            'prescriptions/static/tests/prescriptions_kanban_mobile_tests.js',
        ],
    }
}
