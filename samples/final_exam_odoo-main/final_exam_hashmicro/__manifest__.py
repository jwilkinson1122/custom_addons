{
    'name': "Final Exam Hashmicro",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'stock', 'product', 'stock', 'purchase','sale_management', 'report_xlsx'],

    # always loaded
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "views/product_views.xml",
        "views/booking_order_config_views.xml",
        "views/booking_order_pivot_views.xml",
        "views/menus.xml",
        "views/fitur_optional/webclient_template_extend.xml",
        "views/fitur_optional/res_user_views.xml",
        "wizard/report_booking_order_pdf/booking_order_pdf_wizard.xml",
        "wizard/report_booking_order_pdf/booking_order_pdf_template.xml",
        "wizard/report_booking_order_excel/report_booking_order_wizard.xml",
        "wizard/fitur_optional/whatsapp_send_message_views.xml",
        "reports/report_action.xml",
        "reports/report_booking_order_customer.xml",
        "reports/payment_report_order/sale_report_wizard_xlsx.xml",
    ],
    'demo': [
        'data/product_demo.xml',
    ],
    'static': {
            'src': 'static/src',
        },

    'installable': True,
    'application': True,
}

