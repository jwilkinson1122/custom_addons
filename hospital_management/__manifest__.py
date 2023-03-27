# -*- coding: utf-8 -*-
{
    'name': "hospital_management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'sale', 'website', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/create_appointment_wizard_view.xml',
        'views/hospital_patient_view.xml',
        'views/hospital_appointment_view.xml',
        'views/sale_order_inherit_view.xml',
        'data/cron.xml',
        'report/reports.xml',
        'templates/mail_template.xml',
        'templates/hospital_appointment_template.xml',
        'templates/index_page.xml',
        'templates/create_page.xml',
        'templates/update_page.xml',
        'templates/homepage_override.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {

        'web.assets_qweb': [
            'hospital_management/static/src/xml/**/*',
        ],

        'web.assets_backend': [
            'hospital_management/static/src/js/field_widget.js',
            'hospital_management/static/src/js/catalog_view.js',
            'hospital_management/static/src/js/catalog_model.js',
            'hospital_management/static/src/js/catalog_controller.js',
            'hospital_management/static/src/js/catalog_renderer.js',
            'hospital_management/static/src/js/mail_widget.js',
            'hospital_management/static/src/scss/field_widget.scss',
            # 'hospital_management/static/src/scss/mail_widget.scss',
        ],

    },


}
