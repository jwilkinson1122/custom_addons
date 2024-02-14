# -*- coding: utf-8 -*-
{
    'name': "NWPL - Orthotic Repair",
    'version': "17.0.0.0.0",
    'description': "Orthotic Repair",
    'summary': "Orthotic Repair",
    'author': 'NWPL',
    'website': "https://www.nwpodiatric.com",
    'category': 'Services',
    'depends': [
        'mail', 
        'pod_prescription_contacts', 
        'project', 
        'hr_timesheet', 
        'product', 
        'sale_management', 
        'stock', 
        'website'
        ],
    'data': [
        'data/sequence_views.xml',
        'data/product_data.xml',
        'data/orthotic_repair_mail_templates.xml',
        'data/website_menu.xml',
        'wizards/repair_technician_views.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/assets.xml',
        'views/orthotic_repair_order_views.xml',
        'views/previous_service_history_views.xml',
        'views/repair_team_views.xml',
        'views/material_of_repair_views.xml',
        'views/orthotic_repair_service_views.xml',
        'views/model_views.xml',
        'views/mro_quotation_views.xml',
        'views/inspection_image_views.xml',
        'views/web_template_views.xml',
        'views/repair_service_views.xml',
        'views/checklist_template_views.xml',
        'views/required_analysis_views.xml',
        'views/diagnosed_problem_views.xml',
        'views/task_orthotic_problem_views.xml',
        'report/mro_report_views.xml',
        'report/delivery_order_report_views.xml',
        'report/product_barcode_labels_report_views.xml',
        'report/inspection_report_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pod_orthotic_repair/static/src/js/repair_location.js',
            'pod_orthotic_repair/static/src/css/theme.css',
        ],
        'web.assets_backend': [
            'pod_orthotic_repair/static/src/xml/template.xml',
            'pod_orthotic_repair/static/src/css/lib/dashboard.css',
            'pod_orthotic_repair/static/src/css/style.scss',
            'pod_orthotic_repair/static/src/js/orthotic_repair_dashboard.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
