# -*- coding: utf-8 -*-
{
    'name': "Tooth select widget",

    'summary': """
        Tooth select widget for Dental practice management software""",

    'description': """
        Tooth select widget.
        Dental practice management software.
    """,

    'author': "Tunisofts, By Malek S, Helmi D",
    'website': "https://www.tunisofts.com/",

    'category': 'widget',
    'version': '17.0.0.0.0',
    'application': True,
    'installable': True,
    'images': ['static/description/demo.gif'],
    'currency': 'EUR',
    'live_test_url': 'https://www.youtube.com/embed/6k6DK_xyf3o',
    'price': 100,
    'licence':'OPL-1',
    'license': 'LGPL-3',


    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'data/tooth_data.xml',
        'data/treatment_action_data.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'tooth_select_widget/static/src/**/*',
        ],

    }
}
