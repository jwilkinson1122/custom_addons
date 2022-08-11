# -*- coding: utf-8 -*-


{
    'name': 'Podiatry Custom Form Fields',
    'version': '15.0.0.0',
    'category': 'Sales',
    'summary': 'Add summary here',
    'description': """
        Add custom field on forms
    """,
    'author': 'NWPL',
    'website': 'https://nwpodiatric.com',
    'depends': ['base', 'sale', 'sale_management'],
    'data': [
        'security/pod_custom_groups.xml',
        'security/ir.model.access.csv',
        'views/pod_custom_field_view.xml',

    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    "images": ['static/description/icon.png'],
    "license": "OPL-1",
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
