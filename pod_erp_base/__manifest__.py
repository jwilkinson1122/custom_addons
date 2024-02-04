# -*- coding: utf-8 -*-
{
    'name': 'ERP Base',
    'version': '17.0.0.0',
    'summary': 'Added some custom functionality to manage podiatry partners',
    'author': 'NWPL',
    'description': """Added some custom functionality to manage podiatry partners.""",
    'category': 'Base',
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        # 'pod_theme',
        'base', 
        'mail', 
        'sale',
        'sale_management', 
        'contacts', 
        'stock',
        ],
    'data': [
        'security/pod_erp_security.xml',
        'security/ir.model.access.csv',
        'data/pod_partner_data.xml',
        'data/pod_location_type_data.xml',

        'views/pod_location_type_views.xml',
        'views/pod_flag_views.xml',
        'views/pod_flag_category_views.xml',

        'views/res_partner_view.xml',

        'views/pod_patient_custom_views.xml',
        'views/pod_patient_views.xml',

        # 'views/pod_contact_type_views.xml',
        # 'views/pod_program_views.xml',
        # 'views/pod_status_views.xml',

        
        'views/sale_order_views.xml',

        # 'views/stock_picking_views.xml',
        # 'views/stock_move_line_views.xml',
        # 'views/stock_picking_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
