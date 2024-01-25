# -*- coding: utf-8 -*-
{
    'name': 'Pod ERP Base',
    'version': '17.0.0.0',
    'summary': 'Added some custom functionality to manage podiatry partners',
    'author': 'NWPL',
    'description': """Added some custom functionality to manage podiatry partners.""",
    'category': 'Base',
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'base', 
        'mail', 
        'sale',
        'sale_management', 
        'contacts', 
        'stock',
        ],
    'data': [
        'security/patients_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/organization_custom_contact.xml',
        'views/practice_custom_contact.xml',
        'views/practitioner_custom_contact.xml',
        'views/patient_custom_contact.xml',
        'views/patient_contact.xml',
        # 'views/contact_type_views.xml',
        # 'views/pod_program_views.xml',
        # 'views/pod_status_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_picking_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
