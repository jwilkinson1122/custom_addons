# -*- coding: utf-8 -*-

{
    'name': "NWPL - Prescriptions Spreadsheet",
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Prescriptions Spreadsheet',
    'description': 'Prescriptions Spreadsheet',
    'depends': ['prescriptions', 'spreadsheet_edition'],
    'data': [
        'data/prescriptions_folder_data.xml',
        'data/res_company_data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/prescriptions_prescription_views.xml',
        'views/spreadsheet_template_views.xml',
        'views/prescriptions_templates_share.xml',
        'views/sharing_templates.xml',
        'views/res_config_settings_views.xml',
        'wizard/save_spreadsheet_template.xml',
    ],
    'demo': [
        'demo/prescriptions_prescription_demo.xml'
    ],

    'installable': True,
    'auto_install': ['prescriptions'],
    'license': 'LGPL-3',
    'assets': {
        'spreadsheet.o_spreadsheet': [
            'prescriptions_spreadsheet/static/src/bundle/**/*.js',
            'prescriptions_spreadsheet/static/src/bundle/**/*.xml',
            ('remove', 'prescriptions_spreadsheet/static/src/bundle/components/control_panel/spreadsheet_breadcrumbs.xml'),
        ],
        'web.assets_backend': [
            'prescriptions_spreadsheet/static/src/bundle/**/*.scss',
            'prescriptions_spreadsheet/static/src/prescriptions_view/**/*',
            'prescriptions_spreadsheet/static/src/spreadsheet_clone_xlsx_dialog/**/*',
            'prescriptions_spreadsheet/static/src/spreadsheet_selector_dialog/**/*',
            'prescriptions_spreadsheet/static/src/spreadsheet_template/**/*',
            'prescriptions_spreadsheet/static/src/helpers.js',
            'prescriptions_spreadsheet/static/src/spreadsheet_action_loader.js',
            'prescriptions_spreadsheet/static/src/view_insertion.js',
            'prescriptions_spreadsheet/static/src/bundle/components/control_panel/spreadsheet_breadcrumbs.xml',
        ],
        'web.assets_tests': [
            'prescriptions_spreadsheet/static/tests/utils/tour.js',
            'prescriptions_spreadsheet/static/tests/tours/*',
        ],
        'web.qunit_suite_tests': [
            'prescriptions_spreadsheet/static/tests/**/*',
        ]
    }
}
