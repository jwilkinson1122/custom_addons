# -*- coding: utf-8 -*-
{
    'name': "Prescription Order",
    'summary': """Prescription Order NWPL""",
    "version": "15.0.1.0.0",
    'description': """Prescription Order NWPL""",
    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",
    'category': 'Sales',
    'depends': [
        'base',
        'resource',
        'helpdesk',
        'website_helpdesk_form',
        'website_helpdesk_livechat',
        'helpdesk_repair',
        'helpdesk_stock',
        'helpdesk_mail_plugin',
        'data_merge_helpdesk',
        'sale', 
        'sale_management', 
        'sale_stock',
        'sale_product_configurator',
        'sale_product_matrix',
        'sale_quotation_builder',
        'stock',
        'product', 
        'product_matrix',
        'uom',
        'mail',
        "account",
        "account_accountant",
        'l10n_us',
        "mail",
        'purchase',
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        "data/ir_sequence_data.xml",
        'wizard/wizard_cancelled.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/work_order_views.xml',
        'views/podiatry_prescription_views.xml',
        'views/actions.xml',
        'views/menu.xml',
        'report/report_work_order.xml',
        'report/report.xml',
        # 'wizard/wizard_cancelled.xml',
    ],
    "assets": {
        "web.assets_backend": [

        ],
    },
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "images": ["static/description/icon.png"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "application": True,
    "installable": True,
    "application": True,
    "auto_install": False,
}