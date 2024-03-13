# -*- coding: utf-8 -*-



{
    'name': 'POS HR Manufacturing',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Link module between pos_hr and pos_manufacturing',
    'description': """
This module adapts the behavior of the PoS when the pos_hr and pos_manufacturing are installed.
""",
    'depends': ['pos_hr', 'pos_manufacturing'],
    'auto_install': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_hr_manufacturing/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
